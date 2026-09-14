from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.portail import (
    DemandePreVerificationReponse,
    DemandePreVerificationRequete,
    VerificationCompteReponse,
    VerificationCompteRequete,
)
from solida.adapters.http.schemas.produits import ProduitCredit
from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.application.use_cases.authenticate_societaire import AuthenticateSocietaire
from solida.application.use_cases.lister_produits import ListerProduits
from solida.application.use_cases.process_societaire_demande import ProcessSocietaireDemande
from solida.domain.errors import IdentiteSocietaireInvalide
from solida.infrastructure.auth.dependencies import client_ip_address
from solida.infrastructure.dependencies import (
    audit_log,
    authenticate_societaire,
    lister_produits,
    process_societaire_demande,
)

router = APIRouter(prefix="/api/v1/portail", tags=["portail"])

TENTATIVES_LIMITE = 3
FENETRE_VERROU = timedelta(hours=5)


def _jeton_bearer(authorization: str | None = Header(default=None)) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail={"code": "session_expiree", "message": "Session expirée, recommencez."},
        )
    return authorization.removeprefix("Bearer ")


@router.post("/verification-compte", response_model=VerificationCompteReponse)
def verification_compte(
    demande: VerificationCompteRequete,
    request: Request,
    use_case: AuthenticateSocietaire = Depends(authenticate_societaire),
    audit: SqlAuditLog = Depends(audit_log),
) -> VerificationCompteReponse:
    ip = client_ip_address(request)
    cle_verrou = f"{demande.numero_compte}:{ip}"
    depuis = datetime.now(UTC) - FENETRE_VERROU
    echecs_recents = audit.compter_evenements_recents("prevalidation_echouee", cle_verrou, depuis)
    if echecs_recents >= TENTATIVES_LIMITE:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Trop de tentatives, réessayez plus tard.",
        )

    try:
        resultat = use_case.execute(demande.numero_compte, demande.montant_dernier_depot)
    except IdentiteSocietaireInvalide:
        audit.enregistrer_evenement(
            "prevalidation_echouee", demande.numero_compte, cle_verrou, {}, ip
        )
        raise

    return VerificationCompteReponse(jeton_session=resultat.jeton_session, prenom=resultat.prenom)


@router.post("/demandes", response_model=DemandePreVerificationReponse)
def demandes(
    demande: DemandePreVerificationRequete,
    jeton: str = Depends(_jeton_bearer),
    use_case: ProcessSocietaireDemande = Depends(process_societaire_demande),
) -> DemandePreVerificationReponse:
    resultat = use_case.execute(
        jeton_session=jeton,
        montant_demande=demande.montant,
        objet_credit=demande.objet,
        duree_mois=demande.duree_mois,
        produit_id=demande.produit_id,
    )
    return DemandePreVerificationReponse(
        issue=resultat.pre_verification.issue,
        message=resultat.pre_verification.message,
        montant_propose=resultat.pre_verification.montant_propose,
        demande_id=resultat.demande_id,
    )


@router.get("/produits", response_model=list[ProduitCredit])
def produits(
    jeton: str = Depends(_jeton_bearer),
    use_case: ListerProduits = Depends(lister_produits),
) -> list[ProduitCredit]:
    """Le sociétaire choisit un produit pour que l'agent l'ait sous les yeux à la
    réception de la demande : le modèle ne s'en sert pas comme feature, mais le taux
    et les bornes de durée qu'il fixe entrent bien dans le calcul du score."""
    return [mappers.produit_to_schema(p) for p in use_case.execute()]
