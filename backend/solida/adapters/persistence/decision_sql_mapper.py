"""Conversion entre les lignes SQL et les décisions du domaine."""

from typing import Any

from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.motif_bascule import MotifBascule
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.points_variable import PointsVariable
from solida.domain.values.score import Score
from solida.domain.values.tranche import TrancheDecision


def decomposition_to_json(points: list[PointsVariable]) -> list[dict[str, Any]]:
    return [{"code_variable": point.code_variable, "points": point.points} for point in points]


def decomposition_from_json(values: list[dict[str, Any]]) -> list[PointsVariable]:
    return [
        PointsVariable(code_variable=value["code_variable"], points=value["points"])
        for value in values
    ]


def result_complement_to_json(decision: DecisionAEnregistrer) -> dict[str, Any]:
    return {
        "motif_mode": decision.motif_mode.value if decision.motif_mode else None,
        "points_de_base": decision.points_de_base,
        "plafond_progressif": decision.plafond_progressif.valeur,
        "trajectoire_progression": [
            {"cycle": step.cycle, "plafond_accessible": step.plafond_accessible.valeur}
            for step in decision.trajectoire_progression
        ],
        "conditions_reexamen": decision.conditions_reexamen,
        "avertissements": decision.avertissements,
    }


def row_to_decision(row: Any, agent_nom: str, agent_agence_id: str | None) -> DecisionEnregistree:
    complement = row.resultat_complementaire
    return DecisionEnregistree(
        decision_id=str(row.decision_id),
        agent_id=str(row.agent_id),
        agent_nom=agent_nom,
        agent_agence_id=agent_agence_id,
        societaire_id=row.societaire_id,
        entree=row.entree,
        features_utilisees=row.features_utilisees,
        probabilite=row.probabilite,
        score=Score(valeur=row.score),
        tranche=TrancheDecision(row.tranche),
        montant_recommande=Montant(valeur=row.montant_recommande),
        mode_calcul=ModeCalcul(row.mode_calcul),
        motif_mode=MotifBascule(complement["motif_mode"]) if complement.get("motif_mode") else None,
        points_de_base=complement["points_de_base"],
        decomposition=decomposition_from_json(row.decomposition),
        plafond_progressif=Montant(valeur=complement["plafond_progressif"]),
        trajectoire_progression=[
            PalierProgression(
                cycle=step["cycle"], plafond_accessible=Montant(valeur=step["plafond_accessible"])
            )
            for step in complement["trajectoire_progression"]
        ],
        conditions_reexamen=complement["conditions_reexamen"],
        avertissements=complement["avertissements"],
        version_modele=row.version_modele,
        version_grille=row.version_grille,
        horodatage=row.horodatage,
    )
