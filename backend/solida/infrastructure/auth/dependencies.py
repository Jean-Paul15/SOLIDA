from collections.abc import Callable, Coroutine

from fastapi import Depends, Request

from solida.adapters.persistence.orm_models import User
from solida.domain.errors import AccesRefuse
from solida.infrastructure.auth.current_user import current_active_user


def require_role(*allowed_roles: str) -> Callable[..., Coroutine[None, None, User]]:
    """Refuse un rôle non autorisé avant d’atteindre le cas d’usage."""

    async def dependency(user: User = Depends(current_active_user)) -> User:
        if user.role not in allowed_roles:
            raise AccesRefuse(f"Le rôle '{user.role}' n'a pas accès à cette action.")
        return user

    return dependency


def client_ip_address(request: Request) -> str | None:
    """Privilégie l’adresse validée par nginx, avec repli pour le développement local."""
    return request.headers.get("x-real-ip") or (request.client.host if request.client else None)
