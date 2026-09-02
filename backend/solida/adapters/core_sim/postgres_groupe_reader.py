from datetime import date, timedelta

from sqlalchemy import Engine, text

from solida.domain.entities.groupe import GroupeCaution, MembreGroupe


class PostgresGroupeReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None:
        membership_query = text("""
            SELECT gie_id FROM societaires WHERE societaire_id = :id AND gie_id IS NOT NULL
        """)
        with self._engine.connect() as connection:
            membership_row = connection.execute(membership_query, {"id": societaire_id}).first()
            if membership_row is None:
                return None
            gie_id = membership_row.gie_id

            group_row = connection.execute(
                text(
                    "SELECT gie_id, taille, date_creation FROM groupes_gie WHERE gie_id = :gie_id"
                ),
                {"gie_id": gie_id},
            ).first()
            if group_row is None:
                return None

            member_rows = connection.execute(
                text("""
                    SELECT a.societaire_id, s.nom_complet, a.role, a.date_entree, a.date_sortie
                    FROM appartenances_gie a
                    JOIN societaires s ON s.societaire_id = a.societaire_id
                    WHERE a.gie_id = :gie_id
                """),
                {"gie_id": gie_id},
            ).all()

            credit_status_rows = connection.execute(
                text("""
                    SELECT DISTINCT ON (societaire_id) societaire_id, statut
                    FROM credits
                    WHERE societaire_id = ANY(:ids)
                    ORDER BY societaire_id, date_deblocage DESC
                """),
                {"ids": [member.societaire_id for member in member_rows]},
            ).all()
            credit_status_by_societaire = {
                status.societaire_id: status.statut for status in credit_status_rows
            }

            called_guarantee_rows = connection.execute(
                text("""
                    SELECT DISTINCT garant_societaire_id
                    FROM garanties
                    WHERE garant_societaire_id = ANY(:ids) AND garantie_appelee = true
                """),
                {"ids": [member.societaire_id for member in member_rows]},
            ).all()
            called_guarantors = {
                guarantee.garant_societaire_id for guarantee in called_guarantee_rows
            }

            other_member_ids = [
                member.societaire_id
                for member in member_rows
                if member.societaire_id != societaire_id
            ]
            resolved_credit_rows = connection.execute(
                text("""
                    SELECT statut FROM credits
                    WHERE societaire_id = ANY(:ids) AND statut IN ('solde', 'en_souffrance')
                """),
                {"ids": other_member_ids},
            ).all()
            exit_count = connection.execute(
                text("""
                    SELECT count(*) AS n FROM appartenances_gie
                    WHERE gie_id = :gie_id AND date_sortie >= :depuis
                """),
                {"gie_id": gie_id, "depuis": date.today() - timedelta(days=365)},
            ).scalar_one()

        resolved_credit_count = len(resolved_credit_rows)
        settled_credit_count = sum(1 for credit in resolved_credit_rows if credit.statut == "solde")
        repayment_rate = (
            settled_credit_count / resolved_credit_count if resolved_credit_count > 0 else None
        )
        active_member_count = sum(1 for member in member_rows if member.date_sortie is None)

        group_status = "actif"
        if active_member_count == 0:
            group_status = "dissous"
        elif repayment_rate is not None and repayment_rate < 0.5:
            group_status = "en_difficulte"

        today = date.today()
        members = [
            MembreGroupe(
                societaire_id=member.societaire_id,
                nom_complet=member.nom_complet,
                role=member.role,
                anciennete_mois=(today.year - member.date_entree.year) * 12
                + today.month
                - member.date_entree.month,
                statut_credit=credit_status_by_societaire.get(member.societaire_id, "aucun_credit"),
                caution_appelee=member.societaire_id in called_guarantors,
            )
            for member in member_rows
            if member.date_sortie is None
        ]

        return GroupeCaution(
            groupe_id=group_row.gie_id,
            nom_groupe=f"Groupement {group_row.gie_id}",
            taille_actuelle=active_member_count,
            date_creation=group_row.date_creation,
            taux_remboursement_groupe=repayment_rate,
            nb_cycles_completes=settled_credit_count,
            nb_credits_anterieurs_soldes=settled_credit_count,
            nb_sorties_12m=exit_count,
            statut=group_status,
            membres=members,
        )
