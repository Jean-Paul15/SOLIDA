from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """Score de credit sur l'echelle PDO. Convention bancaire : score eleve = risque faible."""

    valeur: float
