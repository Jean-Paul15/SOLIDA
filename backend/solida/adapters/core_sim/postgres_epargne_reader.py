from datetime import date

from sqlalchemy import Engine, text

from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.mouvement_epargne import MouvementEpargne


class PostgresEpargneReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None:
        query = text("""
            SELECT compte_id, societaire_id, solde_epargne_moyen_6m, nb_mois_avec_depot_12m,
                   croissance_epargne_12m, volatilite_epargne
            FROM comptes_epargne WHERE societaire_id = :id
        """)
        with self._engine.connect() as connection:
            row = connection.execute(query, {"id": societaire_id}).first()
        if row is None:
            return None
        return CompteEpargne(
            compte_id=row.compte_id,
            societaire_id=row.societaire_id,
            solde_moyen_6m=round(row.solde_epargne_moyen_6m),
            nb_mois_avec_depot_12m=row.nb_mois_avec_depot_12m,
            croissance_12m=float(row.croissance_epargne_12m),
            volatilite=float(row.volatilite_epargne),
        )

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]:
        query = text("""
            SELECT m.mouvement_id, m.compte_id, m.date_operation, m.sens, m.montant,
                   m.type_operation
            FROM mouvements_epargne m
            JOIN comptes_epargne c ON c.compte_id = m.compte_id
            WHERE c.societaire_id = :id AND m.date_operation >= :depuis
            ORDER BY m.date_operation
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"id": societaire_id, "depuis": depuis})
            return [
                MouvementEpargne(
                    mouvement_id=row.mouvement_id,
                    compte_id=row.compte_id,
                    date_operation=row.date_operation,
                    sens=row.sens,
                    montant=round(row.montant),
                    type_operation=row.type_operation,
                )
                for row in rows
            ]
