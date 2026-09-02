from datetime import UTC, datetime

from solida.adapters.http.mappers.commun import _decomposition_to_schema
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree


def _resultat_scoring_commun(
    decision: DecisionAEnregistrer, horodatage: str
) -> schema_scoring.ScoringResult:
    montant_demande = decision.entree.get("montant_demande")
    montant_demande_int = montant_demande if isinstance(montant_demande, int) else 0
    return schema_scoring.ScoringResult(
        decision_id=decision.decision_id,
        societaire_id=decision.societaire_id,
        score=decision.score.valeur,
        tranche=decision.tranche.value,
        montant_recommande=decision.montant_recommande.valeur,
        montant_demande=montant_demande_int,
        mode_calcul=decision.mode_calcul.value,
        motif_mode=decision.motif_mode.value if decision.motif_mode else None,
        decomposition=_decomposition_to_schema(decision.decomposition, decision.features_utilisees),
        points_de_base=decision.points_de_base,
        plafond_progressif=decision.plafond_progressif.valeur,
        trajectoire_progression=[
            schema_scoring.PalierProgression(
                cycle=p.cycle, plafond_accessible=p.plafond_accessible.valeur
            )
            for p in decision.trajectoire_progression
        ],
        conditions_reexamen=decision.conditions_reexamen,
        version_modele=decision.version_modele,
        version_grille=decision.version_grille,
        horodatage=horodatage,
        avertissements=decision.avertissements,
    )


def decision_to_resultat_scoring(decision: DecisionEnregistree) -> schema_scoring.ScoringResult:
    return _resultat_scoring_commun(decision, decision.horodatage.isoformat())


def decision_a_enregistrer_to_resultat_scoring(
    decision: DecisionAEnregistrer,
) -> schema_scoring.ScoringResult:
    """Pour une prévisualisation, pas encore persistée : pas de vrai horodatage
    d'enregistrement, on affiche celui du calcul."""
    return _resultat_scoring_commun(decision, datetime.now(UTC).isoformat())
