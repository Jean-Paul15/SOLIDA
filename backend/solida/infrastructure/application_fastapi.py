from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from solida.domain.errors import (
    AccesRefuse,
    DomainError,
    DonneesInsuffisantes,
    DureeDemandeeInvalide,
    IdentiteSocietaireInvalide,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    ScorecardImmuable,
    SocietaireIntrouvable,
    SurEndettement,
    VersionGrilleDejaExistante,
)
from solida.infrastructure.access_logging_middleware import AccessLoggingMiddleware
from solida.infrastructure.logging_config import configure_logging
from solida.infrastructure.routers import (
    auth,
    health,
    notifications,
    parametrage,
    portail,
    produits,
    registre,
    scoring,
    societaires,
)

# Traduction des exceptions du domaine vers un statut HTTP : la plus specifique
# d'abord, DomainError servant de repli pour toute regle metier non listee ici.
_ERROR_STATUSES: list[tuple[type[DomainError], int, str]] = [
    (AccesRefuse, 403, "acces_refuse"),
    (SocietaireIntrouvable, 404, "introuvable"),
    (ProduitIntrouvable, 404, "introuvable"),
    (DonneesInsuffisantes, 422, "donnees_insuffisantes"),
    (MontantDemandeInvalide, 422, "montant_invalide"),
    (DureeDemandeeInvalide, 422, "duree_invalide"),
    (SurEndettement, 422, "sur_endettement"),
    (VersionGrilleDejaExistante, 409, "version_deja_existante"),
    (ScorecardImmuable, 422, "scorecard_immuable"),
    (IdentiteSocietaireInvalide, 401, "identite_invalide"),
    (DomainError, 400, "regle_metier"),
]


def create_application() -> FastAPI:
    configure_logging()
    application = FastAPI(title="SOLIDA API")
    application.add_middleware(AccessLoggingMiddleware)
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(societaires.router)
    application.include_router(scoring.router)
    application.include_router(registre.router)
    application.include_router(parametrage.router)
    application.include_router(produits.router)
    application.include_router(portail.router)
    application.include_router(notifications.router)

    for error_class, status, code in _ERROR_STATUSES:

        def handle_error(
            request: Request,
            error: DomainError,
            status: int = status,
            code: str = code,
        ) -> JSONResponse:
            return JSONResponse(status_code=status, content={"code": code, "message": str(error)})

        application.exception_handler(error_class)(handle_error)

    return application


app = create_application()
