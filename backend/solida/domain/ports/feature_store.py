from datetime import date
from typing import Protocol

from solida.domain.values.features import FeaturesIndividuelles, FeaturesSolidaires


class FeatureStore(Protocol):
    """Simplification assumée pour cette passe, sans pipeline batch : `ecrire_lot`
    n'existe pas encore ici. Les features sont calculées à la demande à partir
    de CORE-SIM, pas lues dans une table de features historisée.
    `date_dernier_rafraichissement` reflète donc l'instant du calcul, pas un
    batch planifié.
    """

    def lire_individuelles(self, societaire_id: str) -> FeaturesIndividuelles | None: ...

    def lire_solidaires(self, societaire_id: str) -> FeaturesSolidaires | None: ...

    def date_dernier_rafraichissement(self, societaire_id: str) -> date | None: ...
