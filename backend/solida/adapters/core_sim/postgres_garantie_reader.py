from sqlalchemy import Engine, text

from solida.domain.entities.garantie import Garantie


class PostgresGarantieReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_garanties(self, societaire_id: str) -> list[Garantie]:
        query = text("""
            SELECT garantie_id, credit_id, type_garantie, garant_societaire_id,
                   beneficiaire_societaire_id, montant_garanti, date_engagement, garantie_appelee
            FROM garanties
            WHERE beneficiaire_societaire_id = :id OR garant_societaire_id = :id
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"id": societaire_id})
            return [
                Garantie(
                    garantie_id=row.garantie_id,
                    credit_id=row.credit_id,
                    type_garantie=row.type_garantie,
                    garant_societaire_id=row.garant_societaire_id,
                    beneficiaire_societaire_id=row.beneficiaire_societaire_id,
                    montant_garanti=round(row.montant_garanti),
                    date_engagement=row.date_engagement,
                    garantie_appelee=bool(row.garantie_appelee),
                )
                for row in rows
            ]
