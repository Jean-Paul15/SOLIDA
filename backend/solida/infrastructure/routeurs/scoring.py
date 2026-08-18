import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.fiche import FicheJustification
from solida.adapters.http.schemas.scoring import EntreeScoring, ResultatScoring
from solida.adapters.pdf.fiche_pdf_generator_weasyprint import WeasyPrintFichePdfGenerator
from solida.adapters.persistence.modeles_sqlalchemy import Utilisateur
from solida.application.use_cases.archiver_fiche import ArchiverFiche
from solida.application.use_cases.generer_fiche import GenererFiche
from solida.application.use_cases.lire_decision import LireDecision
from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.domain.erreurs import AccesRefuse
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.demande import ActualisationSituation, DemandeScoring
from solida.infrastructure.auth import current_active_user, require_role
from solida.infrastructure.dependances import (
    archiver_fiche,
    fiche_pdf_generator,
    generer_fiche,
    lire_decision,
    scorer_demande,
)

router = APIRouter(prefix="/api/v1/scoring", tags=["scoring"])


def _erreur_introuvable() -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail={
            "code": "introuvable",
            "message": "Aucune décision ne correspond à cet identifiant.",
        },
    )


def _valider_decision_id(decision_id: str) -> None:
    """Rejette explicitement un format invalide avant toute requête DB : sans ça,
    `uuid.UUID(...)` lève une `ValueError` non interceptée plus bas dans la pile,
    remontant en 500 générique au lieu d'un 422 propre."""
    try:
        uuid.UUID(decision_id)
    except ValueError as erreur:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "identifiant_invalide",
                "message": "L'identifiant de décision n'est pas un UUID valide.",
            },
        ) from erreur


def _demande_depuis_entree(entree: EntreeScoring) -> DemandeScoring:
    return DemandeScoring(
        societaire_id=entree.societaire_id,
        produit_id=entree.produit_id,
        montant_demande=entree.montant_demande,
        duree_demandee_mois=entree.duree_demandee_mois,
        objet_credit=entree.objet_credit,
        groupe_id=entree.groupe_id,
        actualisation=(
            ActualisationSituation(
                revenu_mensuel_declare=entree.actualisation.revenu_mensuel_declare,
                charges_mensuelles=entree.actualisation.charges_mensuelles,
                nb_personnes_a_charge=entree.actualisation.nb_personnes_a_charge,
            )
            if entree.actualisation
            else None
        ),
    )


@router.post("/previsualiser", response_model=ResultatScoring)
def previsualiser(
    entree: EntreeScoring,
    utilisateur: Utilisateur = Depends(require_role("agent")),
    cas_usage: ScorerDemande = Depends(scorer_demande),
) -> ResultatScoring:
    agent_agence_id = utilisateur.agence_id if utilisateur.role == "agent" else None
    decision = cas_usage.previsualiser(
        _demande_depuis_entree(entree),
        entree_brute=entree.model_dump(),
        agent_id=str(utilisateur.id),
        agent_nom=utilisateur.nom_complet,
        agent_agence_id=agent_agence_id,
    )
    return mappers.decision_a_enregistrer_vers_resultat_scoring(decision)


@router.post("/confirmer", response_model=ResultatScoring, status_code=status.HTTP_201_CREATED)
def confirmer(
    entree: EntreeScoring,
    utilisateur: Utilisateur = Depends(require_role("agent")),
    cas_usage: ScorerDemande = Depends(scorer_demande),
) -> ResultatScoring:
    agent_agence_id = utilisateur.agence_id if utilisateur.role == "agent" else None
    decision = cas_usage.confirmer(
        _demande_depuis_entree(entree),
        entree_brute=entree.model_dump(),
        agent_id=str(utilisateur.id),
        agent_nom=utilisateur.nom_complet,
        agent_agence_id=agent_agence_id,
    )
    return mappers.decision_vers_resultat_scoring(decision)


def _verifier_acces_agence(utilisateur: Utilisateur, decision: DecisionEnregistree) -> None:
    if utilisateur.role == "agent" and decision.agent_agence_id != utilisateur.agence_id:
        raise AccesRefuse("Cette décision ne concerne pas votre agence.")


@router.get("/{decision_id}", response_model=ResultatScoring)
def lire(
    decision_id: str,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: LireDecision = Depends(lire_decision),
) -> ResultatScoring:
    _valider_decision_id(decision_id)
    decision = cas_usage.executer(decision_id)
    if decision is None:
        raise _erreur_introuvable()
    _verifier_acces_agence(utilisateur, decision)
    return mappers.decision_vers_resultat_scoring(decision)


@router.get("/{decision_id}/fiche", response_model=FicheJustification)
def fiche(
    decision_id: str,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: GenererFiche = Depends(generer_fiche),
) -> FicheJustification:
    _valider_decision_id(decision_id)
    resultat = cas_usage.executer(decision_id)
    if resultat is None:
        raise _erreur_introuvable()
    decision, entete = resultat
    _verifier_acces_agence(utilisateur, decision)
    return mappers.fiche_vers_schema(decision, entete)


@router.get("/{decision_id}/fiche/pdf")
def fiche_pdf(
    decision_id: str,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: GenererFiche = Depends(generer_fiche),
    generateur: WeasyPrintFichePdfGenerator = Depends(fiche_pdf_generator),
) -> Response:
    _valider_decision_id(decision_id)
    resultat = cas_usage.executer(decision_id)
    if resultat is None:
        raise _erreur_introuvable()
    decision, entete = resultat
    _verifier_acces_agence(utilisateur, decision)
    pdf = generateur.generer(decision, entete)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="fiche-{decision_id}.pdf"'},
    )


@router.post("/{decision_id}/archiver")
def archiver(
    decision_id: str,
    utilisateur: Utilisateur = Depends(require_role("agent")),
    cas_usage: ArchiverFiche = Depends(archiver_fiche),
) -> dict[str, str]:
    _valider_decision_id(decision_id)
    fiche_id = cas_usage.executer(
        decision_id,
        archive_par=utilisateur.nom_complet,
        agent_role=utilisateur.role,
        agent_agence_id=utilisateur.agence_id,
    )
    if fiche_id is None:
        raise _erreur_introuvable()
    return {"fiche_id": fiche_id}
