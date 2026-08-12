from dataclasses import dataclass

from solida.domain.erreurs import ScorecardImmuable
from solida.domain.ports.grille import DepotGrille
from solida.domain.values.grille import ConfigurationGrille


@dataclass(frozen=True)
class LireGrilleActive:
    depot: DepotGrille

    def executer(self) -> ConfigurationGrille:
        return self.depot.lire_active()


@dataclass(frozen=True)
class ModifierGrille:
    """La validation des seuils (marge/LGD positives, multiplicateurs croissants) est déjà
    portée par `ParametresGrille.__post_init__` : construire la configuration avant d'appeler
    ce cas d'usage suffit à la déclencher, pas besoin de la dupliquer ici.
    """

    depot: DepotGrille

    def executer(self, nouvelle_configuration: ConfigurationGrille) -> ConfigurationGrille:
        active = self.depot.lire_active()
        nouveau = nouvelle_configuration.scorecard
        actuel = active.scorecard
        # pdo/score_reference/odds_reference ne sont plus editables depuis l'ecran Politique de
        # credit (transmis inchanges, cf. 03-MODELE/10-politique-credit-decisions-en-attente.md) :
        # le serveur impose la meme invariance, sinon un appel API direct pouvait les changer sans
        # aucun garde-fou de calibration.
        if (
            nouveau.pdo != actuel.pdo
            or nouveau.score_reference != actuel.score_reference
            or nouveau.odds_reference != actuel.odds_reference
        ):
            raise ScorecardImmuable(
                "pdo, score_reference et odds_reference ne peuvent pas être modifiés tant que "
                "le modèle réel n'est pas calibré."
            )
        return self.depot.enregistrer_nouvelle_version(nouvelle_configuration)
