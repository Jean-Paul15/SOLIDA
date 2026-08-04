from typing import Protocol

from solida.domain.values.grille import ConfigurationGrille


class DepotGrille(Protocol):
    """La grille est versionnée, jamais modifiée en place : `enregistrer_nouvelle_version`
    ajoute une ligne et la marque active, elle ne réécrit jamais une version passée — une
    décision déjà prise doit rester reproductible avec la version qui était active alors.
    """

    def lire_active(self) -> ConfigurationGrille: ...

    def enregistrer_nouvelle_version(
        self, configuration: ConfigurationGrille
    ) -> ConfigurationGrille: ...
