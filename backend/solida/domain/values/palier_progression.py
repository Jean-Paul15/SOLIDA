from dataclasses import dataclass

from solida.domain.values.montant import Montant


@dataclass(frozen=True)
class PalierProgression:
    """Plafond accessible a un cycle futur si le societaire rembourse sans incident."""

    cycle: int
    plafond_accessible: Montant
