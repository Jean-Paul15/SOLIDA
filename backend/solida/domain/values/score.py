from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """Score de crédit sur l'échelle PDO. Convention bancaire : score élevé = risque faible."""

    valeur: float
