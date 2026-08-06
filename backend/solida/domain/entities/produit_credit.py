from dataclasses import dataclass


@dataclass(frozen=True)
class ProduitCredit:
    """Référentiel CORE-SIM : identité et valeurs de référence d'un produit de crédit.

    `montant_max` ici est la valeur de référence du réseau, pas le plafond
    réellement appliqué au scoring — celui-ci vit dans `grille_decision.seuils`
    (ajustable par la supervision, voir `ParametresProgressif.plafonds_produits`).
    """

    produit_id: str
    libelle: str
    type_garantie: str
    montant_min: int
    montant_max: int
    duree_min_mois: int
    duree_max_mois: int
    taux_annuel: float
