from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard


@dataclass(frozen=True)
class ConfigurationGrille:
    """Une version complète de la grille : ce qui est chargé depuis `grille_decision`
    et ce que `scorer_demande` a besoin de connaître pour une décision reproductible.
    """

    version_grille: str
    grille: ParametresGrille
    progressif: ParametresProgressif
    scorecard: ParametresScorecard
    auteur: str
    date_activation: datetime
    active: bool
    classification_objets: Mapping[str, str] = field(default_factory=dict)
    """`objet_credit` -> `divisible` | `indivisible` | `mixte`. Vide tant qu'aucune table
    métier réelle n'a été fournie (`modelisation/docs/decisions-socle.md`) : un objet
    absent de cette table n'est jamais deviné divisible."""
    objets_implicites_produits: Mapping[str, str] = field(default_factory=dict)
    """`produit_id` -> `objet_credit`, pour les produits dont le nom détermine déjà l'usage
    (ex. un futur "Crédit agricole" pourrait impliquer `intrants_agricoles`). Vide par défaut :
    aucun produit du catalogue CORE-SIM n'a d'objet imposé tant que la coopérative n'a pas
    confirmé cette correspondance produit par produit — jamais devinée depuis le libellé.
    Un produit absent de cette table redemande l'objet au sociétaire (liste fermée,
    `ObjetCredit`), exactement comme aujourd'hui."""
