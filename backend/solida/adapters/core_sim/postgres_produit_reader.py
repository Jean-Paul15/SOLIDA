from sqlalchemy import Engine, text

from solida.domain.entities.produit_credit import ProduitCredit


class PostgresProduitReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_produits(self) -> list[ProduitCredit]:
        """Lit le catalogue CORE-SIM, distinct des plafonds de la grille SOLIDA."""
        query = text("""
            SELECT produit_id, libelle, segment, type_garantie, montant_min, montant_max,
                   duree_min_mois, duree_max_mois, taux_annuel
            FROM produits_credit ORDER BY produit_id
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(query)
            return [
                ProduitCredit(
                    produit_id=row.produit_id,
                    libelle=row.libelle,
                    segment=row.segment,
                    type_garantie=row.type_garantie,
                    montant_min=round(row.montant_min),
                    montant_max=round(row.montant_max),
                    duree_min_mois=row.duree_min_mois,
                    duree_max_mois=row.duree_max_mois,
                    taux_annuel=float(row.taux_annuel),
                )
                for row in rows
            ]
