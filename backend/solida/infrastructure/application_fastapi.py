from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from solida.adapters.http import auth_dependencies
from solida.domain.erreurs import (
    AccesRefuse,
    DonneesInsuffisantes,
    DureeDemandeeInvalide,
    ErreurDomaine,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    ScorecardImmuable,
    SocietaireIntrouvable,
    SurEndettement,
    VersionGrilleDejaExistante,
)
from solida.infrastructure.auth import current_active_user as infra_current_active_user
from solida.infrastructure.journalisation import configure_logging
from solida.infrastructure.middleware_journalisation import AccessLoggingMiddleware
from solida.infrastructure.routeurs import (
    auth,
    health,
    parametrage,
    produits,
    registre,
    scoring,
    societaires,
)

# Traduction des exceptions du domaine vers un statut HTTP : la plus specifique
# d'abord, ErreurDomaine servant de repli pour toute regle metier non listee ici.
_STATUTS_PAR_ERREUR: list[tuple[type[ErreurDomaine], int, str]] = [
    (AccesRefuse, 403, "acces_refuse"),
    (SocietaireIntrouvable, 404, "introuvable"),
    (ProduitIntrouvable, 404, "introuvable"),
    (DonneesInsuffisantes, 422, "donnees_insuffisantes"),
    (MontantDemandeInvalide, 422, "montant_invalide"),
    (DureeDemandeeInvalide, 422, "duree_invalide"),
    (SurEndettement, 422, "sur_endettement"),
    (VersionGrilleDejaExistante, 409, "version_deja_existante"),
    (ScorecardImmuable, 422, "scorecard_immuable"),
    (ErreurDomaine, 400, "regle_metier"),
]


def creer_application() -> FastAPI:
    configure_logging()
    application = FastAPI(title="SOLIDA API")
    application.add_middleware(AccessLoggingMiddleware)
    # Le stub `auth_dependencies.current_active_user` (adapters/http/) est ce que les
    # routeurs importent : seule cette racine de composition a le droit de connaitre a la
    # fois le stub et l'implementation reelle (infrastructure/auth.py), donc c'est ici,
    # et seulement ici, que l'override est cable.
    application.dependency_overrides[auth_dependencies.current_active_user] = (
        infra_current_active_user
    )
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(societaires.router)
    application.include_router(scoring.router)
    application.include_router(registre.router)
    application.include_router(parametrage.router)
    application.include_router(produits.router)

    for classe_erreur, statut, code in _STATUTS_PAR_ERREUR:

        def gerer(
            requete: Request,
            erreur: ErreurDomaine,
            statut: int = statut,
            code: str = code,
        ) -> JSONResponse:
            return JSONResponse(status_code=statut, content={"code": code, "message": str(erreur)})

        application.exception_handler(classe_erreur)(gerer)

    return application


app = creer_application()
