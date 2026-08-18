from sqlalchemy import Engine, text

from solida.domain.entities.produit_credit import ProduitCredit


class PostgresProduitReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def charger_produits(self) -> list[ProduitCredit]:
        """Référentiel des produits de crédit — table CORE-SIM, pas les plafonds
        appliqués (ceux-ci vivent dans `grille_decision`, ajustables par la
        supervision sans repasser par le générateur)."""
        requete = text("""
            SELECT produit_id, libelle, type_garantie, montant_min, montant_max,
                   duree_min_mois, duree_max_mois, taux_annuel
            FROM produits_credit ORDER BY produit_id
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete)
            return [
                ProduitCredit(
                    produit_id=ligne.produit_id,
                    libelle=ligne.libelle,
                    type_garantie=ligne.type_garantie,
                    montant_min=round(ligne.montant_min),
                    montant_max=round(ligne.montant_max),
                    duree_min_mois=ligne.duree_min_mois,
                    duree_max_mois=ligne.duree_max_mois,
                    taux_annuel=float(ligne.taux_annuel),
                )
                for ligne in lignes
            ]
