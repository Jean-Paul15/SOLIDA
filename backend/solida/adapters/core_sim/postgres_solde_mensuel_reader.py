from datetime import date

from solida_modelisation.features_epargne import SoldeMensuelEpargne
from sqlalchemy import Engine, text

from solida.adapters.core_sim._dates import vers_date


class PostgresSoldeMensuelReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_soldes_mensuels(self, societaire_id: str, avant: date) -> list[SoldeMensuelEpargne]:
        query = text("""
            SELECT mois, solde_fin_mois, total_depots, total_retraits
            FROM solde_mensuel_epargne
            WHERE societaire_id = :id AND type_compte = 'epargne_libre' AND mois <= :avant
            ORDER BY mois
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"id": societaire_id, "avant": avant})
            return [
                SoldeMensuelEpargne(
                    mois=vers_date(row.mois),
                    solde_fin_mois=float(row.solde_fin_mois),
                    total_depots=float(row.total_depots),
                    total_retraits=float(row.total_retraits),
                )
                for row in rows
            ]
