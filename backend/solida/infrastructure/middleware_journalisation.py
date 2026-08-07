import logging
import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from solida.infrastructure.auth import adresse_ip_client

logger = logging.getLogger("solida.acces")

_CHEMINS_SANS_BRUIT = {"/api/v1/sante"}
"""Sonde de santé interrogée en continu par le healthcheck Docker : au niveau INFO, elle
noierait le journal d'accès sous des lignes sans valeur diagnostique."""


class MiddlewareJournalisationAcces(BaseHTTPMiddleware):
    """Remplace le journal d'accès en texte brut d'uvicorn (désactivé via `--no-access-log`,
    voir le Dockerfile) par une ligne structurée par requête, avec la même adresse IP fiable
    que le journal d'audit métier (`adresse_ip_client`)."""

    async def dispatch(
        self, requete: Request, appel_suivant: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        debut = time.perf_counter()
        reponse = await appel_suivant(requete)
        if requete.url.path in _CHEMINS_SANS_BRUIT:
            return reponse
        duree_ms = round((time.perf_counter() - debut) * 1000, 1)
        logger.info(
            "requete_http",
            extra={
                "champs": {
                    "methode": requete.method,
                    "chemin": requete.url.path,
                    "statut": reponse.status_code,
                    "duree_ms": duree_ms,
                    "adresse_ip": adresse_ip_client(requete),
                }
            },
        )
        return reponse
