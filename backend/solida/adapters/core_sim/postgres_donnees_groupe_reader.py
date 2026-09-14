from solida_modelisation.features_groupe import (
    AppartenanceGie,
    CautionGroupe,
    CreditGroupeAnterieur,
    EcheanceGroupe,
)
from sqlalchemy import Engine, text

from solida.adapters.core_sim._dates import vers_date
from solida.domain.values.features import DonneesGroupeBrutes

# Un crédit de groupe est un crédit dont l'emprunteur officiel est le GIE : `gie_id`
# renseigné sur le crédit ET garantie `caution_solidaire_gie` — même définition que
# `modelisation.features._credits_de_groupe`, jamais inférée du seul segment.
_CREDITS_GROUPE_CTE = """
    credits_groupe AS (
        SELECT c.credit_id, c.date_deblocage, c.date_issue, c.statut
        FROM credits c
        JOIN garanties g ON g.credit_id = c.credit_id AND g.type_garantie = 'caution_solidaire_gie'
        WHERE c.gie_id = :gie_id
    )
"""


class PostgresDonneesGroupeReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_donnees_groupe(self, gie_id: str) -> DonneesGroupeBrutes | None:
        with self._engine.connect() as connection:
            groupe_row = connection.execute(
                text("SELECT date_creation FROM groupes_gie WHERE gie_id = :gie_id"),
                {"gie_id": gie_id},
            ).first()
            if groupe_row is None:
                return None

            appartenance_rows = connection.execute(
                text(
                    "SELECT societaire_id, date_entree, date_sortie "
                    "FROM appartenances_gie WHERE gie_id = :gie_id"
                ),
                {"gie_id": gie_id},
            ).all()

            credit_rows = connection.execute(
                text(f"WITH {_CREDITS_GROUPE_CTE} SELECT * FROM credits_groupe"),
                {"gie_id": gie_id},
            ).all()

            echeance_rows = connection.execute(
                text(f"""
                    WITH {_CREDITS_GROUPE_CTE}
                    SELECT e.credit_id, e.date_paiement_reelle, e.jours_retard
                    FROM echeances e
                    JOIN credits_groupe cg ON cg.credit_id = e.credit_id
                    WHERE e.niveau_enregistrement = 'groupe'
                """),
                {"gie_id": gie_id},
            ).all()

            caution_rows = connection.execute(
                text(f"""
                    WITH {_CREDITS_GROUPE_CTE}
                    SELECT g.credit_id, g.garantie_appelee
                    FROM garanties g
                    JOIN credits_groupe cg ON cg.credit_id = g.credit_id
                    WHERE g.type_garantie = 'caution_solidaire_gie'
                """),
                {"gie_id": gie_id},
            ).all()

        return DonneesGroupeBrutes(
            date_creation=vers_date(groupe_row.date_creation),
            appartenances=[
                AppartenanceGie(
                    societaire_id=row.societaire_id,
                    date_entree=vers_date(row.date_entree),
                    date_sortie=None if row.date_sortie is None else vers_date(row.date_sortie),
                )
                for row in appartenance_rows
            ],
            credits_anterieurs=[
                CreditGroupeAnterieur(
                    credit_id=row.credit_id,
                    date_deblocage=vers_date(row.date_deblocage),
                    date_issue=None if row.date_issue is None else vers_date(row.date_issue),
                    statut=row.statut,
                )
                for row in credit_rows
            ],
            echeances_groupe=[
                EcheanceGroupe(
                    credit_id=row.credit_id,
                    date_paiement_reelle=(
                        None
                        if row.date_paiement_reelle is None
                        else vers_date(row.date_paiement_reelle)
                    ),
                    jours_retard=(None if row.jours_retard is None else float(row.jours_retard)),
                )
                for row in echeance_rows
            ],
            cautions_anterieures=[
                CautionGroupe(credit_id=row.credit_id, garantie_appelee=bool(row.garantie_appelee))
                for row in caution_rows
            ],
        )
