from dataclasses import dataclass

from solida.domain.values.montant import Montant


@dataclass(frozen=True)
class PalierProgression:
    """Plafond accessible à un cycle futur si le sociétaire rembourse sans incident."""

    cycle: int
    plafond_accessible: Montant
