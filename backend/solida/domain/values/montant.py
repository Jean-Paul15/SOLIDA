from dataclasses import dataclass


@dataclass(frozen=True)
class Montant:
    """Montant en FCFA. Toujours entier, jamais negatif ni flottant."""

    valeur: int

    def __post_init__(self) -> None:
        if self.valeur < 0:
            raise ValueError("Un montant ne peut pas etre negatif.")
