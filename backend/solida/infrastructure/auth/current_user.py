import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi_users import FastAPIUsers
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from solida.adapters.persistence.orm_models import User
from solida.infrastructure.auth.cookie import authentication_backend, cookie_transport
from solida.infrastructure.auth.manager import get_user_manager
from solida.infrastructure.auth.session import get_token_db

MAX_INACTIVITY_DURATION = timedelta(minutes=15)
"""Expiration par inactivité vérifiée côté serveur à chaque requête."""

_fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [authentication_backend])
_active_user_dependency = _fastapi_users.current_user(active=True)


async def current_active_user(
    request: Request,
    user: User = Depends(_active_user_dependency),
    token_db: SQLAlchemyAccessTokenDatabase = Depends(get_token_db),
) -> User:
    """Ajoute une expiration serveur par inactivité à l'authentification fastapi-users."""
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
    return user
