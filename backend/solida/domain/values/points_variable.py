from dataclasses import dataclass


@dataclass(frozen=True)
class PointsVariable:
    """Contribution en points d'une variable à l'écart entre le score et les points de base."""

    code_variable: str
    points: float
