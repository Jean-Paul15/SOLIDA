from dataclasses import dataclass
from datetime import datetime

from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif import ParametresProgressif
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
