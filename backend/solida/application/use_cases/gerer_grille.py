from dataclasses import dataclass, replace

from solida.domain.errors import ScorecardImmuable
from solida.domain.ports.grille import GrilleRepository
from solida.domain.values.grille import ConfigurationGrille


@dataclass(frozen=True)
class LireGrilleActive:
    grille_repository: GrilleRepository

    def execute(self) -> ConfigurationGrille:
        return self.grille_repository.lire_active()


@dataclass(frozen=True)
class ModifierGrille:
    """La validation des seuils (marge/LGD positives, multiplicateurs croissants) est déjà
    portée par `ParametresGrille.__post_init__` : construire la configuration avant d'appeler
    ce cas d'usage suffit à la déclencher, pas besoin de la dupliquer ici.
    """

    grille_repository: GrilleRepository

    def execute(self, nouvelle_configuration: ConfigurationGrille) -> ConfigurationGrille:
        active = self.grille_repository.lire_active()
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
        # classification_objets et objets_implicites_produits ne sont pas exposes par le schema
        # HTTP de cet endpoint (aucun ecran ne les edite) : sans ce report explicite, chaque
        # enregistrement depuis l'ecran Politique de credit les reinitialiserait silencieusement
        # a {} (valeur par defaut du value object), effacant une table que seule la supervision
        # peut renseigner par un autre canal.
        configuration_a_enregistrer = replace(
            nouvelle_configuration,
            classification_objets=active.classification_objets,
            objets_implicites_produits=active.objets_implicites_produits,
        )
        return self.grille_repository.enregistrer_nouvelle_version(configuration_a_enregistrer)
