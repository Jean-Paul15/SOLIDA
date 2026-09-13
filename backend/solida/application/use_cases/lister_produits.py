from dataclasses import dataclass

from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.grille import GrilleRepository


@dataclass(frozen=True)
class ListerProduits:
    """Expose le catalogue CORE-SIM sans plafond de décision par produit."""

    core_sim_reader: CoreSimReader
    grille_repository: GrilleRepository

    def execute(self) -> list[ProduitCredit]:
        return self.core_sim_reader.charger_produits()
