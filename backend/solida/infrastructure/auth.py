import uuid
from collections.abc import AsyncGenerator, Callable, Coroutine
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
from solida.domain.erreurs import AccesRefuse
from solida.infrastructure.config import Configuration

_FICHIER_MOTS_DE_PASSE_COURANTS = Path(__file__).with_name("mots_de_passe_courants.txt")

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

    async def changer_mot_de_passe(
        self, utilisateur: Utilisateur, nouveau_mot_de_passe: str
    ) -> None:
        hachage = self.password_helper.hash(nouveau_mot_de_passe)
        await self.user_db.update(
            utilisateur,
            {
                "hashed_password": hachage,
                "doit_changer_mot_de_passe": False,
                "mot_de_passe_modifie_le": datetime.now(UTC),
            },
        )


async def obtenir_gestionnaire_utilisateurs(
    bdd_utilisateurs: SQLAlchemyUserDatabase = Depends(obtenir_bdd_utilisateurs),
) -> AsyncGenerator[GestionnaireUtilisateurs, None]:
    yield GestionnaireUtilisateurs(bdd_utilisateurs)


@lru_cache(maxsize=1)
def charger_mots_de_passe_courants() -> frozenset[str]:
    lignes = _FICHIER_MOTS_DE_PASSE_COURANTS.read_text(encoding="utf-8").splitlines()
    return frozenset(ligne.strip().lower() for ligne in lignes if ligne.strip())


async def revoquer_jetons_utilisateur(session: AsyncSession, utilisateur_id: uuid.UUID) -> None:
    """Détruit tous les jetons actifs d'un utilisateur — une seule session à la fois,
    et un changement de mot de passe invalide les sessions ouvertes ailleurs."""
    await session.execute(delete(AccessToken).where(AccessToken.user_id == utilisateur_id))
    await session.commit()


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

DUREE_INACTIVITE_MAX = timedelta(minutes=15)
"""Expiration par inactivité, vérifiée côté serveur à chaque requête — un minuteur
côté client seul se contourne (l'attaquant qui a volé la session simule l'activité)."""


def adresse_ip_client(requete: Request) -> str | None:
    """`X-Real-IP` : posé par nginx sur toute requête proxifiée vers l'API (seul point
    d'entrée public, voir `infra/nginx/nginx.conf`), donc jamais falsifiable par le client
    lui-même. `request.client.host` ne sert qu'en développement local, quand l'API est
    appelée directement sans passer par nginx."""
    return requete.headers.get("x-real-ip") or (requete.client.host if requete.client else None)

_utilisateur_actif_brut = fastapi_users.current_user(active=True)


async def current_active_user(
    requete: Request,
    utilisateur: Utilisateur = Depends(_utilisateur_actif_brut),
    bdd_jetons: SQLAlchemyAccessTokenDatabase = Depends(obtenir_bdd_jetons),
) -> Utilisateur:
    """Comme `fastapi_users.current_user(active=True)`, avec en plus l'expiration par
    inactivité : au-delà de `DUREE_INACTIVITE_MAX` sans requête, la session est détruite
    même si elle n'a pas atteint sa durée de vie absolue de `DUREE_SESSION_SECONDES`."""
    jeton_str = requete.cookies.get(transport_cookie.cookie_name)
    jeton = await bdd_jetons.get_by_token(jeton_str) if jeton_str else None
    if jeton is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalide.")

    maintenant = datetime.now(UTC)
    if maintenant - jeton.derniere_activite_le > DUREE_INACTIVITE_MAX:
        await bdd_jetons.delete(jeton)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Session expirée par inactivité, reconnectez-vous."
        )

    await bdd_jetons.update(jeton, {"derniere_activite_le": maintenant})
    return utilisateur


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
