from dataclasses import dataclass
from datetime import UTC, date, datetime

from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.domain.entities.societaire import Societaire
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.score import Score
from solida.domain.values.tranche import TrancheDecision


def _decision(
    decision_id: str, societaire_id: str, agent_agence_id: str | None
) -> DecisionEnregistree:
    return DecisionEnregistree(
        decision_id=decision_id,
        agent_id="agent-1",
        agent_nom="Agent Test",
        agent_agence_id=agent_agence_id,
        societaire_id=societaire_id,
        entree={},
        features_utilisees={},
        probabilite=0.09,
        score=Score(valeur=554),
        tranche=TrancheDecision.ACCORD,
        montant_recommande=Montant(valeur=100000),
        mode_calcul=ModeCalcul.SOCLE_SEUL,
        motif_mode=None,
        points_de_base=554,
        decomposition=[],
        plafond_progressif=Montant(valeur=100000),
        trajectoire_progression=[],
        conditions_reexamen=[],
        avertissements=[],
        version_modele="v1",
        version_grille="v1",
        horodatage=datetime.now(UTC),
    )


def _societaire(societaire_id: str, agence: str) -> Societaire:
    return Societaire(
        societaire_id=societaire_id,
        numero_membre="100000",
        nom_complet="Test Societaire",
        agence=agence,
        date_adhesion=date(2020, 1, 1),
        anciennete_mois=48,
        segment="individuel",
        age=35,
        zone="urbain",
        nb_personnes_a_charge=2,
        niveau_instruction=None,
        parts_sociales_montant=10000,
        revenu_mensuel_declare=100000,
        groupe_id=None,
        a_credit_en_cours=False,
    )


@dataclass
class _DecisionRepositoryFactice:
    decisions: list[DecisionEnregistree]

    def lister(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> list[DecisionEnregistree]:
        return self.decisions

    def compter(self, agence_id: str | None) -> int:
        return len(self.decisions)


@dataclass
class _LecteurFactice:
    agence_par_societaire: dict[str, str]

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        agence = self.agence_par_societaire.get(societaire_id)
        return _societaire(societaire_id, agence) if agence else None


def test_decision_hors_agence_de_lagent_est_exclue_meme_si_le_depot_la_renvoie() -> None:
    """`DecisionRepository.lister` filtre par l'agence de l'AGENT (seule donnée disponible côté SQL,
    CORE-SIM étant une base séparée jamais jointe) : une décision historique où le sociétaire
    n'appartient pas à la même agence que l'agent qui l'a notée doit être revalidée et exclue,
    pas seulement affichée avec une étiquette d'agence différente (voir la note dans
    `lister_decisions.py`).
    """
    decisions = [
        _decision("D1", "SOC-1", agent_agence_id="CAI-00"),
        _decision("D2", "SOC-2", agent_agence_id="CAI-00"),
    ]
    cas_usage = ListerDecisions(
        decision_repository=_DecisionRepositoryFactice(decisions),
        lecteur=_LecteurFactice({"SOC-1": "CAI-00", "SOC-2": "CAI-07"}),
    )

    affichees, total = cas_usage.execute("CAI-00", limite=20, decalage=0)

    assert [a.decision.decision_id for a in affichees] == ["D1"]
    assert total == 2  # le compte brut du dépôt n'est pas corrigé, limite connue (voir commentaire)


def test_superviseur_sans_filtre_agence_voit_tout() -> None:
    decisions = [
        _decision("D1", "SOC-1", agent_agence_id=None),
        _decision("D2", "SOC-2", agent_agence_id=None),
    ]
    cas_usage = ListerDecisions(
        decision_repository=_DecisionRepositoryFactice(decisions),
        lecteur=_LecteurFactice({"SOC-1": "CAI-00", "SOC-2": "CAI-07"}),
    )

    affichees, _ = cas_usage.execute(None, limite=20, decalage=0)

    assert [a.decision.decision_id for a in affichees] == ["D1", "D2"]
