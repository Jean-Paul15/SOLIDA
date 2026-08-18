import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import cast

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, exceptions
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from solida.adapters.persistence.modeles_sqlalchemy import AccessToken, Utilisateur
from solida.infrastructure.config import Configuration

_COMMON_PASSWORDS_FILE = Path(__file__).with_name("mots_de_passe_courants.txt")

SESSION_DURATION_SECONDS = 8 * 60 * 60
"""Session révocable de 8 heures — une journée de travail en agence."""

_config = Configuration()

_async_engine = create_async_engine(_config.solida_database_url_async)
_session_factory = async_sessionmaker(_async_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session


async def get_user_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, Utilisateur)


async def get_token_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SQLAlchemyAccessTokenDatabase, None]:
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


class UserManager(UUIDIDMixin, BaseUserManager[Utilisateur, uuid.UUID]):
    reset_password_token_secret = _config.secret_auth
    verification_token_secret = _config.secret_auth

    async def _get_by_identifier(self, identifiant: str) -> Utilisateur | None:
        # BaseUserManager type user_db en BaseUserDatabase abstrait ; on sait qu'il
        # s'agit toujours du SQLAlchemyUserDatabase injecte par get_user_manager.
        user_db = cast(SQLAlchemyUserDatabase[Utilisateur, uuid.UUID], self.user_db)
        statement = select(Utilisateur).where(Utilisateur.identifiant == identifiant)
        result = await user_db.session.execute(statement)
        return result.scalar_one_or_none()

    async def authenticate_by_identifier(
        self, identifiant: str, mot_de_passe: str
    ) -> Utilisateur | None:
        """Équivalent de `authenticate()`, mais par `identifiant` plutôt que par e-mail.

        Reprend la mitigation de `authenticate()` : hacher un mot de passe même
        quand l'identifiant n'existe pas, pour ne pas révéler par le temps de
        réponse si un identifiant est valide.
        """
        utilisateur = await self._get_by_identifier(identifiant)
        if utilisateur is None:
            self.password_helper.hash(mot_de_passe)
            return None

        verifie, updated_hash = self.password_helper.verify_and_update(
            mot_de_passe, utilisateur.hashed_password
        )
        if not verifie:
            return None
        if updated_hash is not None:
            await self.user_db.update(utilisateur, {"hashed_password": updated_hash})
        return utilisateur

    async def get_by_identifier(self, identifiant: str) -> Utilisateur:
        utilisateur = await self._get_by_identifier(identifiant)
        if utilisateur is None:
            raise exceptions.UserNotExists()
        return utilisateur

    async def change_password(self, utilisateur: Utilisateur, nouveau_mot_de_passe: str) -> None:
        password_hash = self.password_helper.hash(nouveau_mot_de_passe)
        await self.user_db.update(
            utilisateur,
            {
                "hashed_password": password_hash,
                "doit_changer_mot_de_passe": False,
                "mot_de_passe_modifie_le": datetime.now(UTC),
            },
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


@lru_cache(maxsize=1)
def load_common_passwords() -> frozenset[str]:
    lines = _COMMON_PASSWORDS_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip().lower() for line in lines if line.strip())


async def revoke_user_tokens(session: AsyncSession, utilisateur_id: uuid.UUID) -> None:
    """Détruit tous les jetons actifs d'un utilisateur — une seule session à la fois,
    et un changement de mot de passe invalide les sessions ouvertes ailleurs."""
    await session.execute(delete(AccessToken).where(AccessToken.user_id == utilisateur_id))
    await session.commit()


cookie_transport = CookieTransport(
    cookie_name="solida_session",
    cookie_max_age=SESSION_DURATION_SECONDS,
    cookie_httponly=True,
    cookie_secure=_config.environnement == "production",
    cookie_samesite="lax",
)


def get_strategy(
    token_db: AccessTokenDatabase[AccessToken] = Depends(get_token_db),
) -> DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken]:
    return DatabaseStrategy(token_db, lifetime_seconds=SESSION_DURATION_SECONDS)


authentication_backend = AuthenticationBackend(
    name="cookie_db",
    transport=cookie_transport,
    get_strategy=get_strategy,
)

fastapi_users = FastAPIUsers[Utilisateur, uuid.UUID](get_user_manager, [authentication_backend])

MAX_INACTIVITY_DURATION = timedelta(minutes=15)
"""Expiration par inactivité, vérifiée côté serveur à chaque requête — un minuteur
côté client seul se contourne (l'attaquant qui a volé la session simule l'activité)."""


_active_user_dependency = fastapi_users.current_user(active=True)


async def current_active_user(
    request: Request,
    utilisateur: Utilisateur = Depends(_active_user_dependency),
    token_db: SQLAlchemyAccessTokenDatabase = Depends(get_token_db),
) -> Utilisateur:
    """Comme `fastapi_users.current_user(active=True)`, avec en plus l'expiration par
    inactivité : au-delà de `MAX_INACTIVITY_DURATION` sans requête, la session est détruite
    même si elle n'a pas atteint sa durée de vie absolue de `SESSION_DURATION_SECONDS`."""
    token_value = request.cookies.get(cookie_transport.cookie_name)
    token = await token_db.get_by_token(token_value) if token_value else None
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalide.")

    now = datetime.now(UTC)
    if now - token.derniere_activite_le > MAX_INACTIVITY_DURATION:
        await token_db.delete(token)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Session expirée par inactivité, reconnectez-vous."
        )

    await token_db.update(token, {"derniere_activite_le": now})
    return utilisateur
