from typing import Protocol

from solida.domain.values.features import ValeurFeature
from solida.domain.values.probabilite import ProbabiliteDefaut


class ScoringModel(Protocol):
    """Contrat d'un modèle explicable, indépendant de son stockage ou de MLflow."""

    def identifiant(self) -> str: ...

    def version(self) -> str: ...

    def variables_attendues(self) -> list[str]: ...

    def predire(self, features: dict[str, ValeurFeature]) -> ProbabiliteDefaut: ...

    def contributions(self, features: dict[str, ValeurFeature]) -> list[tuple[str, float]]:
        """Retourne `(code_variable, contribution_log_odds)` pour chaque variable.

        Liste vide acceptée pour un modèle qui n'a pas de décomposition par variable :
        `decomposer_en_points` produit alors des points de base égaux au score, sans
        contribution ; un cas dégénéré légitime du mécanisme générique, pas un cas
        particulier codé en dur.
        """
        ...
