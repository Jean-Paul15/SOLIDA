import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.fiche import FicheJustification
from solida.adapters.http.schemas.scoring import ScoringInput, ScoringResult
from solida.adapters.pdf.fiche_pdf_generator_weasyprint import WeasyPrintFichePdfGenerator
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.archiver_fiche import ArchiverFiche
from solida.application.use_cases.generer_fiche import GenererFiche
from solida.application.use_cases.lire_decision import LireDecision
from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.domain.errors import AccesRefuse
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.demande import ActualisationSituation, DemandeScoring
from solida.infrastructure.auth.dependencies import current_active_user, require_role
from solida.infrastructure.dependencies import (
    archiver_fiche,
    fiche_pdf_generator,
    generer_fiche,
    lire_decision,
    scorer_demande,
)

router = APIRouter(prefix="/api/v1/scoring", tags=["scoring"])


def _not_found_error() -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail={
            "code": "introuvable",
            "message": "Aucune décision ne correspond à cet identifiant.",
        },
    )


def _validate_decision_id(decision_id: str) -> None:
    """Convertit les UUID invalides en erreur HTTP 422 plutôt qu'en erreur serveur."""
    try:
        uuid.UUID(decision_id)
    except ValueError as erreur:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "code": "identifiant_invalide",
                "message": "L'identifiant de décision n'est pas un UUID valide.",
            },
        ) from erreur


def _to_demande(scoring_input: ScoringInput) -> DemandeScoring:
    return DemandeScoring(
        societaire_id=scoring_input.societaire_id,
        produit_id=scoring_input.produit_id,
        montant_demande=scoring_input.montant_demande,
        duree_demandee_mois=scoring_input.duree_demandee_mois,
        objet_credit=scoring_input.objet_credit,
        groupe_id=scoring_input.groupe_id,
        actualisation=(
            ActualisationSituation(
                revenu_mensuel_declare=scoring_input.actualisation.revenu_mensuel_declare,
                charges_mensuelles=scoring_input.actualisation.charges_mensuelles,
                nb_personnes_a_charge=scoring_input.actualisation.nb_personnes_a_charge,
            )
            if scoring_input.actualisation
            else None
        ),
    )


@router.post("/preview", response_model=ScoringResult)
def preview(
    scoring_input: ScoringInput,
    user: User = Depends(require_role("agent")),
    use_case: ScorerDemande = Depends(scorer_demande),
) -> ScoringResult:
    agent_agence_id = user.agence_id if user.role == "agent" else None
    decision = use_case.preview(
        _to_demande(scoring_input),
        raw_input=scoring_input.model_dump(),
        agent_id=str(user.id),
        agent_nom=user.nom_complet,
        agent_agence_id=agent_agence_id,
    )
    return mappers.decision_a_enregistrer_to_resultat_scoring(decision)


@router.post("/confirm", response_model=ScoringResult, status_code=status.HTTP_201_CREATED)
def confirm(
    scoring_input: ScoringInput,
    user: User = Depends(require_role("agent")),
    use_case: ScorerDemande = Depends(scorer_demande),
) -> ScoringResult:
    agent_agence_id = user.agence_id if user.role == "agent" else None
    decision = use_case.confirm(
        _to_demande(scoring_input),
        raw_input=scoring_input.model_dump(),
        agent_id=str(user.id),
        agent_nom=user.nom_complet,
        agent_agence_id=agent_agence_id,
    )
    return mappers.decision_to_resultat_scoring(decision)


def _validate_agency_access(user: User, decision: DecisionEnregistree) -> None:
    if user.role == "agent" and decision.agent_agence_id != user.agence_id:
        raise AccesRefuse("Cette décision ne concerne pas votre agence.")


@router.get("/{decision_id}", response_model=ScoringResult)
def lire(
    decision_id: str,
    user: User = Depends(current_active_user),
    use_case: LireDecision = Depends(lire_decision),
) -> ScoringResult:
    _validate_decision_id(decision_id)
    decision = use_case.execute(decision_id)
    if decision is None:
        raise _not_found_error()
    _validate_agency_access(user, decision)
    return mappers.decision_to_resultat_scoring(decision)


@router.get("/{decision_id}/fiche", response_model=FicheJustification)
def fiche(
    decision_id: str,
    user: User = Depends(current_active_user),
    use_case: GenererFiche = Depends(generer_fiche),
) -> FicheJustification:
    _validate_decision_id(decision_id)
    result = use_case.execute(decision_id)
    if result is None:
        raise _not_found_error()
    decision, header = result
    _validate_agency_access(user, decision)
    return mappers.fiche_to_schema(decision, header)


@router.get("/{decision_id}/fiche/pdf")
def fiche_pdf(
    decision_id: str,
    user: User = Depends(current_active_user),
    use_case: GenererFiche = Depends(generer_fiche),
    generator: WeasyPrintFichePdfGenerator = Depends(fiche_pdf_generator),
) -> Response:
    _validate_decision_id(decision_id)
    result = use_case.execute(decision_id)
    if result is None:
        raise _not_found_error()
    decision, header = result
    _validate_agency_access(user, decision)
    pdf = generator.generer(decision, header)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="fiche-{decision_id}.pdf"'},
    )


@router.post("/{decision_id}/archive")
def archive(
    decision_id: str,
    user: User = Depends(require_role("agent")),
    use_case: ArchiverFiche = Depends(archiver_fiche),
) -> dict[str, str]:
    _validate_decision_id(decision_id)
    fiche_id = use_case.execute(
        decision_id,
        archive_par=user.nom_complet,
        agent_role=user.role,
        agent_agence_id=user.agence_id,
    )
    if fiche_id is None:
        raise _not_found_error()
    return {"fiche_id": fiche_id}
