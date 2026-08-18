from sqlalchemy import Engine, text

from solida.domain.entities.garantie import Garantie


class PostgresGarantieReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def charger_garanties(self, societaire_id: str) -> list[Garantie]:
        requete = text("""
            SELECT garantie_id, credit_id, type_garantie, garant_societaire_id,
                   beneficiaire_societaire_id, montant_garanti, date_engagement, garantie_appelee
            FROM garanties
            WHERE beneficiaire_societaire_id = :id OR garant_societaire_id = :id
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id})
            return [
                Garantie(
                    garantie_id=ligne.garantie_id,
                    credit_id=ligne.credit_id,
                    type_garantie=ligne.type_garantie,
                    garant_societaire_id=ligne.garant_societaire_id,
                    beneficiaire_societaire_id=ligne.beneficiaire_societaire_id,
                    montant_garanti=round(ligne.montant_garanti),
                    date_engagement=ligne.date_engagement,
                    garantie_appelee=bool(ligne.garantie_appelee),
                )
                for ligne in lignes
            ]
