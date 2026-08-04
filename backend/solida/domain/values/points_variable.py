from dataclasses import dataclass


@dataclass(frozen=True)
class PointsVariable:
    """Contribution en points d'une variable a l'ecart entre le score et les points de base."""

    code_variable: str
    points: float
