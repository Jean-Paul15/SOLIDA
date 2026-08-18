import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.motif_bascule import MotifBascule
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.points_variable import PointsVariable
from solida.domain.values.score import Score
from solida.domain.values.tranche import TrancheDecision


def _decomposition_vers_json(points: list[PointsVariable]) -> list[dict[str, Any]]:
    return [{"code_variable": p.code_variable, "points": p.points} for p in points]


def _decomposition_depuis_json(valeurs: list[dict[str, Any]]) -> list[PointsVariable]:
    return [PointsVariable(code_variable=v["code_variable"], points=v["points"]) for v in valeurs]


def _resultat_complementaire_vers_json(decision: DecisionAEnregistrer) -> dict[str, Any]:
    return {
        "motif_mode": decision.motif_mode.value if decision.motif_mode else None,
        "points_de_base": decision.points_de_base,
        "plafond_progressif": decision.plafond_progressif.valeur,
        "trajectoire_progression": [
            {"cycle": p.cycle, "plafond_accessible": p.plafond_accessible.valeur}
            for p in decision.trajectoire_progression
        ],
        "conditions_reexamen": decision.conditions_reexamen,
        "avertissements": decision.avertissements,
    }


def _ligne_vers_decision(
    ligne: Any, agent_nom: str, agent_agence_id: str | None
) -> DecisionEnregistree:
    complement = ligne.resultat_complementaire
    return DecisionEnregistree(
        decision_id=str(ligne.decision_id),
        agent_id=str(ligne.agent_id),
        agent_nom=agent_nom,
        agent_agence_id=agent_agence_id,
        societaire_id=ligne.societaire_id,
        entree=ligne.entree,
        features_utilisees=ligne.features_utilisees,
        probabilite=ligne.probabilite,
        score=Score(valeur=ligne.score),
        tranche=TrancheDecision(ligne.tranche),
        montant_recommande=Montant(valeur=ligne.montant_recommande),
        mode_calcul=ModeCalcul(ligne.mode_calcul),
        motif_mode=(
            MotifBascule(complement["motif_mode"]) if complement.get("motif_mode") else None
        ),
        points_de_base=complement["points_de_base"],
        decomposition=_decomposition_depuis_json(ligne.decomposition),
        plafond_progressif=Montant(valeur=complement["plafond_progressif"]),
        trajectoire_progression=[
            PalierProgression(
                cycle=p["cycle"], plafond_accessible=Montant(valeur=p["plafond_accessible"])
            )
            for p in complement["trajectoire_progression"]
        ],
        conditions_reexamen=complement["conditions_reexamen"],
        avertissements=complement["avertissements"],
        version_modele=ligne.version_modele,
        version_grille=ligne.version_grille,
        horodatage=ligne.horodatage,
    )


class SqlDecisionRepository:
    """Implémente `DecisionRepository` contre `decision_scoring` (schéma `solida`).

    N'exécute jamais d'UPDATE ni de DELETE sur cette table : le déclencheur
    `decision_scoring_insertion_seule` en base le refuserait de toute façon,
    mais ce dépôt n'essaie même pas.
    """

    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def enregistrer(self, decision: DecisionAEnregistrer) -> DecisionEnregistree:
        # Un double-clic ou un retry reseau renvoie la meme requete (memes societaire/agent/
        # entree) en l'espace de quelques secondes : plutot que d'inserer un doublon, on
        # renvoie la decision deja persistee la plus recente.
        requete_doublon = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE d.societaire_id = :societaire_id AND d.agent_id = :agent_id
              AND d.entree = :entree AND d.horodatage > now() - interval '10 seconds'
            ORDER BY d.horodatage DESC LIMIT 1
        """).bindparams(bindparam("entree", type_=JSONB))

        # bindparams(type_=JSONB) : psycopg3 n'adapte pas un dict Python tout seul, il faut
        # lui dire explicitement de le serialiser en JSONB plutot que de tenter un %s brut.
        instruction = text("""
            INSERT INTO decision_scoring
                (decision_id, societaire_id, agent_id, entree, features_utilisees,
                 probabilite, score, tranche, montant_recommande, mode_calcul,
                 decomposition, resultat_complementaire, version_modele, version_grille)
            VALUES
                (:decision_id, :societaire_id, :agent_id, :entree, :features_utilisees,
                 :probabilite, :score, :tranche, :montant_recommande, :mode_calcul,
                 :decomposition, :resultat_complementaire, :version_modele, :version_grille)
            RETURNING *
        """).bindparams(
            bindparam("entree", type_=JSONB),
            bindparam("features_utilisees", type_=JSONB),
            bindparam("decomposition", type_=JSONB),
            bindparam("resultat_complementaire", type_=JSONB),
        )
        with self._moteur.connect() as connexion:
            doublon = connexion.execute(
                requete_doublon,
                {
                    "societaire_id": decision.societaire_id,
                    "agent_id": uuid.UUID(decision.agent_id),
                    "entree": decision.entree,
                },
            ).first()
            if doublon is not None:
                return _ligne_vers_decision(doublon, doublon.agent_nom, doublon.agent_agence_id)

            ligne = connexion.execute(
                instruction,
                {
                    "decision_id": uuid.UUID(decision.decision_id),
                    "societaire_id": decision.societaire_id,
                    "agent_id": uuid.UUID(decision.agent_id),
                    "entree": decision.entree,
                    "features_utilisees": decision.features_utilisees,
                    "probabilite": decision.probabilite,
                    "score": decision.score.valeur,
                    "tranche": decision.tranche.value,
                    "montant_recommande": decision.montant_recommande.valeur,
                    "mode_calcul": decision.mode_calcul.value,
                    "decomposition": _decomposition_vers_json(decision.decomposition),
                    "resultat_complementaire": _resultat_complementaire_vers_json(decision),
                    "version_modele": decision.version_modele,
                    "version_grille": decision.version_grille,
                },
            ).one()
            connexion.commit()

        return _ligne_vers_decision(ligne, decision.agent_nom, decision.agent_agence_id)

    def lire(self, decision_id: str) -> DecisionEnregistree | None:
        requete = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE d.decision_id = :id
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete, {"id": uuid.UUID(decision_id)}).first()
        if ligne is None:
            return None
        return _ligne_vers_decision(ligne, ligne.agent_nom, ligne.agent_agence_id)

    def lister(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> list[DecisionEnregistree]:
        requete = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE CAST(:agence_id AS text) IS NULL OR u.agence_id = :agence_id
            ORDER BY d.horodatage DESC
            LIMIT :limite OFFSET :decalage
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(
                requete, {"agence_id": agence_id, "limite": limite, "decalage": decalage}
            )
            return [
                _ligne_vers_decision(ligne, ligne.agent_nom, ligne.agent_agence_id)
                for ligne in lignes
            ]

    def compter(self, agence_id: str | None) -> int:
        requete = text("""
            SELECT count(*) FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE CAST(:agence_id AS text) IS NULL OR u.agence_id = :agence_id
        """)
        with self._moteur.connect() as connexion:
            return connexion.execute(requete, {"agence_id": agence_id}).scalar_one()

    def existe_decision_accordee_depuis(
        self, societaire_id: str, depuis: datetime, entree_actuelle: dict[str, object]
    ) -> bool:
        # entree IS DISTINCT FROM : exclut un simple retry de la meme demande (double-clic,
        # retry reseau), deja couvert par la deduplication de `enregistrer` ci-dessus.
        requete = text("""
            SELECT 1 FROM decision_scoring
            WHERE societaire_id = :societaire_id
              AND tranche IN ('accord', 'accord_sous_condition')
              AND horodatage >= :depuis
              AND entree IS DISTINCT FROM :entree_actuelle
            LIMIT 1
        """).bindparams(bindparam("entree_actuelle", type_=JSONB))
        with self._moteur.connect() as connexion:
            return (
                connexion.execute(
                    requete,
                    {
                        "societaire_id": societaire_id,
                        "depuis": depuis,
                        "entree_actuelle": entree_actuelle,
                    },
                ).first()
                is not None
            )
