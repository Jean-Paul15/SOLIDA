from dataclasses import dataclass


@dataclass(frozen=True)
class ProbabiliteDefaut:
    """Probabilité de défaut, strictement entre 0 et 1.

    Les bornes exclues (0 et 1) évitent une division par zéro ou un log(0) lors
    du passage en log-odds dans la scorecard.
    """

    valeur: float

    def __post_init__(self) -> None:
        if not (0.0 < self.valeur < 1.0):
            raise ValueError("Une probabilité de défaut doit être strictement entre 0 et 1.")
