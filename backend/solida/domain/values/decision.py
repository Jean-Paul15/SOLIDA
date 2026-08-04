from dataclasses import dataclass
from datetime import datetime

from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.motif_bascule import MotifBascule
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.points_variable import PointsVariable
from solida.domain.values.score import Score
from solida.domain.values.tranche import TrancheDecision


@dataclass(frozen=True)
class DecisionAEnregistrer:
    """Ce que `scorer_demande` transmet au dépôt pour persistance.

    `entree` et `features_utilisees` restent des dictionnaires bruts (JSON-ables) : le domaine
    n'a pas besoin d'en interpréter le contenu, seulement de le faire transiter intact pour
    l'audit — ce sont les seules exceptions au typage fort des value objects dans ce fichier.
    """

    decision_id: str
    agent_id: str
    agent_nom: str
    agent_agence_id: str | None
    societaire_id: str
    entree: dict[str, object]
    features_utilisees: dict[str, float]
    probabilite: float
    score: Score
    tranche: TrancheDecision
    montant_recommande: Montant
    mode_calcul: ModeCalcul
    motif_mode: MotifBascule | None
    points_de_base: float
    decomposition: list[PointsVariable]
    plafond_progressif: Montant
    trajectoire_progression: list[PalierProgression]
    conditions_reexamen: list[str]
    avertissements: list[str]
    version_modele: str
    version_grille: str


@dataclass(frozen=True)
class DecisionEnregistree(DecisionAEnregistrer):
    """Même contenu, complété par ce que seule la base connaît une fois la ligne écrite."""

    horodatage: datetime


@dataclass(frozen=True)
class DecisionRegistreAffichee:
    """`DecisionEnregistree` enrichie du nom et de l'agence du sociétaire (CORE-SIM),
    pour l'écran de registre — `decision_scoring` ne connaît le sociétaire que par son
    identifiant, pas par son nom.
    """

    decision: DecisionEnregistree
    societaire_nom: str
    agence: str
