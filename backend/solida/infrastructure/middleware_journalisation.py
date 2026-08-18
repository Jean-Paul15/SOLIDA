import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from solida.adapters.http.auth_dependencies import client_ip_address

logger = logging.getLogger("solida.acces")

_QUIET_PATHS = {"/api/v1/health"}
"""Sonde de santé interrogée en continu par le healthcheck Docker : au niveau INFO, elle
noierait le journal d'accès sous des lignes sans valeur diagnostique."""


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    """Remplace le journal d'accès en texte brut d'uvicorn (désactivé via `--no-access-log`,
    voir le Dockerfile) par une ligne structurée par requête, avec la même adresse IP fiable
    que le journal d'audit métier (`client_ip_address`)."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        if request.url.path in _QUIET_PATHS:
            return response
        duration_ms = round((time.perf_counter() - start_time) * 1000, 1)
        logger.info(
            "requete_http",
            extra={
                "champs": {
                    "methode": request.method,
                    "chemin": request.url.path,
                    "statut": response.status_code,
                    "duree_ms": duration_ms,
                    "adresse_ip": client_ip_address(request),
                }
            },
        )
        return response
