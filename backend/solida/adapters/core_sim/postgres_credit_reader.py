from datetime import date
from typing import Any

from sqlalchemy import Engine, text

from solida.domain.entities.credit import Credit


def _capital_restant_du(
    montant_octroye: int, statut: str, date_deblocage: date, duree_mois: int, today: date
) -> int:
    """Approxime le capital restant dû.

    CORE-SIM ne fournit pas d'échéancier : la valeur reste une estimation d'affichage.
    Un crédit en souffrance est traité comme impayé en totalité, faute de remboursement partiel.
    """
    if statut == "solde":
        return 0
    if statut == "en_souffrance":
        return montant_octroye
    elapsed_months = max(
        0, (today.year - date_deblocage.year) * 12 + today.month - date_deblocage.month
    )
    remaining_fraction = max(0.0, 1.0 - min(elapsed_months, duree_mois) / duree_mois)
    return round(montant_octroye * remaining_fraction)


def _row_to_credit(row: Any, today: date) -> Credit:
    date_deblocage: date = row.date_deblocage
    duree_mois: int = row.duree_mois
    statut: str = row.statut
    return Credit(
        credit_id=row.credit_id,
        societaire_id=row.societaire_id,
        produit_id=row.produit_id,
        date_deblocage=date_deblocage,
        date_echeance_prevue=row.date_issue,
        duree_mois=duree_mois,
        numero_cycle=row.numero_cycle,
        montant_octroye=row.montant_octroye,
        statut=statut,
        jours_retard_max=(None if row.jours_retard_max is None else round(row.jours_retard_max)),
        capital_restant_du=_capital_restant_du(
            row.montant_octroye, statut, date_deblocage, duree_mois, today
        ),
    )


class PostgresCreditReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        query = text("""
            SELECT credit_id, societaire_id, produit_id, date_deblocage, date_issue, duree_mois,
                   numero_cycle, montant_octroye, statut, jours_retard_max
            FROM credits WHERE societaire_id = :id ORDER BY date_deblocage DESC
        """)
        today = date.today()
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"id": societaire_id})
            return [_row_to_credit(row, today) for row in rows]
