from dataclasses import dataclass, replace

from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.grille import GrilleRepository


@dataclass(frozen=True)
class ListerProduits:
    """Applique les plafonds de la grille active au catalogue CORE-SIM."""

    core_sim_reader: CoreSimReader
    grille_repository: GrilleRepository

    def execute(self) -> list[ProduitCredit]:
        produits = self.core_sim_reader.charger_produits()
        plafonds = self.grille_repository.lire_active().progressif.plafonds_produits
        return [
            replace(p, montant_max=plafonds[p.produit_id].valeur) if p.produit_id in plafonds else p
            for p in produits
        ]
