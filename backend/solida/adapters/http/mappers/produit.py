from solida.adapters.http.schemas import produits as schema_produits
from solida.domain.entities.produit_credit import ProduitCredit


def produit_to_schema(produit: ProduitCredit) -> schema_produits.ProduitCredit:
    return schema_produits.ProduitCredit(
        produit_id=produit.produit_id,
        libelle=produit.libelle,
        type_garantie=produit.type_garantie,
        montant_min=produit.montant_min,
        montant_max=produit.montant_max,
        duree_min_mois=produit.duree_min_mois,
        duree_max_mois=produit.duree_max_mois,
        taux_annuel=produit.taux_annuel,
    )
