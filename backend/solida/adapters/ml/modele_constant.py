from solida.domain.values.probabilite import ProbabiliteDefaut

VERSION = "constant-0.1.0"


class ModeleConstant:
    """Substitut du modèle réel : renvoie une probabilité de défaut fixe.

    Ce n'est pas un modèle déguisé : littéralement une constante, pour rester
    sans ambiguïté hors du périmètre modèle tant que le vrai modèle (EBM
    entraîné) n'existe pas. Permet à toute la chaîne (scorecard, grille,
    cascade, plafond progressif, persistance, HTTP) d'être construite et
    testée dès maintenant.
    """

    def __init__(self, probabilite_constante: float = 0.09) -> None:
        # 0.09 : taux de creances en souffrance cible du generateur
        # (config.yaml, taux_defaut_cible), pas une valeur arbitraire.
        self._probabilite = ProbabiliteDefaut(probabilite_constante)

    def identifiant(self) -> str:
        return "modele_constant"

    def version(self) -> str:
        return VERSION

    def variables_attendues(self) -> list[str]:
        return []

    def predire(self, features: dict[str, float]) -> ProbabiliteDefaut:
        return self._probabilite

    def contributions(self, features: dict[str, float]) -> list[tuple[str, float]]:
        return []
