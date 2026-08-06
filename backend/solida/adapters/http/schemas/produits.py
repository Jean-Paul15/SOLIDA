from pydantic import BaseModel


class ProduitCredit(BaseModel):
    produit_id: str
    libelle: str
    type_garantie: str
    montant_min: int
    montant_max: int
    duree_min_mois: int
    duree_max_mois: int
    taux_annuel: float
