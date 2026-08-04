from dataclasses import dataclass

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
        return self.depot.enregistrer_nouvelle_version(nouvelle_configuration)
