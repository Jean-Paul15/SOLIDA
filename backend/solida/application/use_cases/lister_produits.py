from dataclasses import dataclass, replace

from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.grille import GrilleRepository


@dataclass(frozen=True)
class ListerProduits:
    """Expose le catalogue CORE-SIM sans plafond de décision par produit, complété par
    l'`objet_implicite` connu de SOLIDA pour les produits qui déterminent déjà l'usage
    (voir `ConfigurationGrille.objets_implicites_produits`)."""

    core_sim_reader: CoreSimReader
    grille_repository: GrilleRepository

    def execute(self) -> list[ProduitCredit]:
        objets_implicites = self.grille_repository.lire_active().objets_implicites_produits
        return [
            replace(produit, objet_implicite=objets_implicites.get(produit.produit_id))
            for produit in self.core_sim_reader.charger_produits()
        ]
