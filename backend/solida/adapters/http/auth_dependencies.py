"""Dépendances FastAPI d'authentification exposées aux routers HTTP (`adapters/http/`).

`current_active_user` est un stub : sa résolution réelle (session DB, cookie, jeton) exige
des bibliothèques techniques (SQLAlchemy, fastapi_users) que `domain`/`adapters` n'ont pas le
droit de connaître (contrat de couches `import-linter`). `infrastructure/application_fastapi.py`
remplace ce stub par l'implémentation réelle (`infrastructure/auth.py`) via
`app.dependency_overrides` au moment de l'assemblage de l'application — seul point qui connaît
les deux côtés. `require_role` ne dépend que de ce stub (jamais directement d'infrastructure) :
un seul override suffit à couvrir toutes les variantes de rôles déjà construites par les
routers.
"""

from collections.abc import Callable, Coroutine

from fastapi import Depends, Request

from solida.adapters.persistence.orm_models import User
from solida.domain.errors import AccesRefuse


def current_active_user() -> User:
    """Stub remplacé par `infrastructure.auth.current_active_user` à l'assemblage de l'app."""
    raise NotImplementedError


def require_role(*allowed_roles: str) -> Callable[..., Coroutine[None, None, User]]:
    """Dépendance FastAPI qui vérifie le rôle à l'endpoint.

    Ne remplace pas la vérification d'agence dans le cas d'usage — les deux
    contrôles sont nécessaires, celui-ci ne fait que refuser un rôle absent de
    la liste avant même d'atteindre le cas d'usage.
    """

    async def dependency(user: User = Depends(current_active_user)) -> User:
        if user.role not in allowed_roles:
            raise AccesRefuse(f"Le rôle '{user.role}' n'a pas accès à cette action.")
        return user

    return dependency


def client_ip_address(request: Request) -> str | None:
    """`X-Real-IP` : posé par nginx sur toute requête proxifiée vers l'API (seul point
    d'entrée public, voir `infra/nginx/nginx.conf`), donc jamais falsifiable par le client
    lui-même. `request.client.host` ne sert qu'en développement local, quand l'API est
    appelée directement sans passer par nginx."""
    return request.headers.get("x-real-ip") or (request.client.host if request.client else None)
