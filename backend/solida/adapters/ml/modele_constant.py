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
        return [
            "nb_mois_avec_depot_12m",
            "ratio_endettement",
            "nb_incidents_anterieurs",
            "anciennete_societaire_mois",
            "ratio_epargne_revenu",
            "ratio_epargne_montant",
        ]

    def predire(self, features: dict[str, float]) -> ProbabiliteDefaut:
        return self._probabilite

    def contributions(self, features: dict[str, float]) -> list[tuple[str, float]]:
        """Décomposition heuristique, PAS un modèle appris.

        `predire()` renvoie une probabilité fixe : le score et la décision ne
        dépendent donc jamais de cette méthode (`scorer_demande.py` calibre `beta_0`
        pour absorber exactement l'écart, invariant vérifié à la persistance). Son
        seul rôle est de peupler la fiche de justification et le graphique de
        facteurs déterminants avec quelque chose de plausible plutôt que vide, en
        attendant le vrai modèle entraîné. Les coefficients ci-dessous sont
        illustratifs (même intuition de signe que le générateur de démonstration,
        `simulateur/config/config.yaml`, jamais ses valeurs) : ce ne sont pas des
        poids appris. À SUPPRIMER intégralement dès qu'un modèle réel existe ; voir
        `docs/backend/03-decisions-provisoires-a-revoir.md`.
        """
        contributions: list[tuple[str, float]] = []
        if "nb_mois_avec_depot_12m" in features:
            contributions.append(
                ("nb_mois_avec_depot_12m", 0.12 * (features["nb_mois_avec_depot_12m"] - 6))
            )
        if "ratio_endettement" in features:
            contributions.append(
                ("ratio_endettement", -1.4 * (features["ratio_endettement"] - 0.35))
            )
        if "nb_incidents_anterieurs" in features:
            contributions.append(
                ("nb_incidents_anterieurs", -0.5 * features["nb_incidents_anterieurs"])
            )
        if "anciennete_societaire_mois" in features:
            contributions.append(
                ("anciennete_societaire_mois", 0.01 * (features["anciennete_societaire_mois"] - 36))
            )
        if "ratio_epargne_revenu" in features:
            contributions.append(
                ("ratio_epargne_revenu", 0.6 * (features["ratio_epargne_revenu"] - 0.3))
            )
        if "ratio_epargne_montant" in features:
            contributions.append(
                ("ratio_epargne_montant", 0.5 * (features["ratio_epargne_montant"] - 0.5))
            )
        return contributions
