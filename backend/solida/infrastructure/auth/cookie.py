import uuid

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from solida.adapters.persistence.orm_models import AccessToken, User
from solida.infrastructure.auth.session import get_token_db
from solida.infrastructure.config import Configuration

SESSION_DURATION_SECONDS = 8 * 60 * 60
"""Session révocable de huit heures, adaptée à une journée de travail en agence."""

_configuration = Configuration()

cookie_transport = CookieTransport(
    cookie_name="solida_session",
    cookie_max_age=SESSION_DURATION_SECONDS,
    cookie_httponly=True,
    cookie_secure=_configuration.environnement == "production",
    cookie_samesite="lax",
)


def get_strategy(
    token_db: AccessTokenDatabase[AccessToken] = Depends(get_token_db),
) -> DatabaseStrategy[User, uuid.UUID, AccessToken]:
    return DatabaseStrategy(token_db, lifetime_seconds=SESSION_DURATION_SECONDS)


authentication_backend = AuthenticationBackend(
    name="cookie_db",
    transport=cookie_transport,
    get_strategy=get_strategy,
)
