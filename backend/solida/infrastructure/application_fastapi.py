from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from solida.adapters.http.routeurs import sante
from solida.domain.erreurs import (
    AccesRefuse,
    DonneesInsuffisantes,
    DureeDemandeeInvalide,
    ErreurDomaine,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    SocietaireIntrouvable,
    SurEndettement,
    VersionGrilleDejaExistante,
)
from solida.infrastructure import routeur_auth
from solida.infrastructure.journalisation import configurer_journalisation
from solida.infrastructure.middleware_journalisation import MiddlewareJournalisationAcces
from solida.infrastructure.routeurs import parametrage, produits, registre, scoring, societaires

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
    (ErreurDomaine, 400, "regle_metier"),
]


def creer_application() -> FastAPI:
    configurer_journalisation()
    application = FastAPI(title="SOLIDA API")
    application.add_middleware(MiddlewareJournalisationAcces)
    application.include_router(sante.routeur)
    application.include_router(routeur_auth.routeur)
    application.include_router(societaires.routeur)
    application.include_router(scoring.routeur)
    application.include_router(registre.routeur)
    application.include_router(parametrage.routeur)
    application.include_router(produits.routeur)

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
