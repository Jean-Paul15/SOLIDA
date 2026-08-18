from typing import Protocol

from solida.domain.values.probabilite import ProbabiliteDefaut


class ScoringModel(Protocol):
    """`ConstantScoringModel` (adapters/ml) est la seule implémentation existante pour
    l'instant : ce port est ce qui permet au modèle réel (EBM entraîné) de
    remplacer `ConstantScoringModel` sans qu'aucun code au-dessus n'en soit informé.
    """

    def identifiant(self) -> str: ...

    def version(self) -> str: ...

    def variables_attendues(self) -> list[str]: ...

    def predire(self, features: dict[str, float]) -> ProbabiliteDefaut: ...

    def contributions(self, features: dict[str, float]) -> list[tuple[str, float]]:
        """Retourne `(code_variable, contribution_log_odds)` pour chaque variable.

        Liste vide acceptée pour un modèle qui n'a pas de décomposition par variable :
        `decomposer_en_points` produit alors des points de base égaux au score, sans
        contribution ; un cas dégénéré légitime du mécanisme générique, pas un cas
        particulier codé en dur.
        """
        ...
