import uuid
from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import cast

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, exceptions
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from solida.adapters.persistence.modeles_sqlalchemy import AccessToken, Utilisateur
from solida.domain.erreurs import AccesRefuse
from solida.infrastructure.config import Configuration

DUREE_SESSION_SECONDES = 8 * 60 * 60
"""Session révocable de 8 heures — une journée de travail en agence."""

_configuration = Configuration()

_moteur_async = create_async_engine(_configuration.solida_database_url_async)
_fabrique_session = async_sessionmaker(_moteur_async, expire_on_commit=False)


async def obtenir_session() -> AsyncGenerator[AsyncSession, None]:
    async with _fabrique_session() as session:
        yield session


async def obtenir_bdd_utilisateurs(
    session: AsyncSession = Depends(obtenir_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, Utilisateur)


async def obtenir_bdd_jetons(
    session: AsyncSession = Depends(obtenir_session),
) -> AsyncGenerator[SQLAlchemyAccessTokenDatabase, None]:
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


class GestionnaireUtilisateurs(UUIDIDMixin, BaseUserManager[Utilisateur, uuid.UUID]):
    reset_password_token_secret = _configuration.secret_auth
    verification_token_secret = _configuration.secret_auth

    async def _par_identifiant(self, identifiant: str) -> Utilisateur | None:
        # BaseUserManager type user_db en BaseUserDatabase abstrait ; on sait qu'il
        # s'agit toujours du SQLAlchemyUserDatabase injecte par obtenir_gestionnaire_utilisateurs.
        bdd_utilisateurs = cast(SQLAlchemyUserDatabase[Utilisateur, uuid.UUID], self.user_db)
        instruction = select(Utilisateur).where(Utilisateur.identifiant == identifiant)
        resultat = await bdd_utilisateurs.session.execute(instruction)
        return resultat.scalar_one_or_none()

    async def authentifier_par_identifiant(
        self, identifiant: str, mot_de_passe: str
    ) -> Utilisateur | None:
        """Équivalent de `authenticate()`, mais par `identifiant` plutôt que par e-mail.

        Reprend la mitigation de `authenticate()` : hacher un mot de passe même
        quand l'identifiant n'existe pas, pour ne pas révéler par le temps de
        réponse si un identifiant est valide.
        """
        utilisateur = await self._par_identifiant(identifiant)
        if utilisateur is None:
            self.password_helper.hash(mot_de_passe)
            return None

        verifie, hachage_mis_a_jour = self.password_helper.verify_and_update(
            mot_de_passe, utilisateur.hashed_password
        )
        if not verifie:
            return None
        if hachage_mis_a_jour is not None:
            await self.user_db.update(utilisateur, {"hashed_password": hachage_mis_a_jour})
        return utilisateur

    async def get_by_identifiant(self, identifiant: str) -> Utilisateur:
        utilisateur = await self._par_identifiant(identifiant)
        if utilisateur is None:
            raise exceptions.UserNotExists()
        return utilisateur


async def obtenir_gestionnaire_utilisateurs(
    bdd_utilisateurs: SQLAlchemyUserDatabase = Depends(obtenir_bdd_utilisateurs),
) -> AsyncGenerator[GestionnaireUtilisateurs, None]:
    yield GestionnaireUtilisateurs(bdd_utilisateurs)


transport_cookie = CookieTransport(
    cookie_name="solida_session",
    cookie_max_age=DUREE_SESSION_SECONDES,
    cookie_httponly=True,
    cookie_secure=_configuration.environnement == "production",
    cookie_samesite="lax",
)


def obtenir_strategie(
    bdd_jetons: AccessTokenDatabase[AccessToken] = Depends(obtenir_bdd_jetons),
) -> DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken]:
    return DatabaseStrategy(bdd_jetons, lifetime_seconds=DUREE_SESSION_SECONDES)


backend_authentification = AuthenticationBackend(
    name="cookie_db",
    transport=transport_cookie,
    get_strategy=obtenir_strategie,
)

fastapi_users = FastAPIUsers[Utilisateur, uuid.UUID](
    obtenir_gestionnaire_utilisateurs, [backend_authentification]
)

current_active_user = fastapi_users.current_user(active=True)


def exige_role(*roles_autorises: str) -> Callable[..., Coroutine[None, None, Utilisateur]]:
    """Dépendance FastAPI qui vérifie le rôle à l'endpoint.

    Ne remplace pas la vérification d'agence dans le cas d'usage — les deux
    contrôles sont nécessaires, celui-ci ne fait que refuser un rôle absent de
    la liste avant même d'atteindre le cas d'usage.
    """

    async def dependance(utilisateur: Utilisateur = Depends(current_active_user)) -> Utilisateur:
        if utilisateur.role not in roles_autorises:
            raise AccesRefuse(
                f"Le rôle '{utilisateur.role}' n'a pas accès à cette action."
            )
        return utilisateur

    return dependance
