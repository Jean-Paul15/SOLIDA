from dataclasses import dataclass, replace

from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.grille import DepotGrille


@dataclass(frozen=True)
class ListerProduits:
    """Fusionne l'identité du catalogue (CORE-SIM, référentiel) avec le plafond
    réellement appliqué (grille active, ajustable par la supervision sans repasser
    par le générateur) : le `montant_max` renvoyé est celui que le scoring opposera
    réellement, pas seulement la valeur de référence du réseau.
    """

    lecteur: LecteurCoreSim
    depot_grille: DepotGrille

    def executer(self) -> list[ProduitCredit]:
        produits = self.lecteur.charger_produits()
        plafonds = self.depot_grille.lire_active().progressif.plafonds_produits
        return [
            replace(p, montant_max=plafonds[p.produit_id].valeur)
            if p.produit_id in plafonds
            else p
            for p in produits
        ]
