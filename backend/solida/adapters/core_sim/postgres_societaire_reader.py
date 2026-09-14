from sqlalchemy import Engine, text

from solida.adapters.core_sim._dates import vers_date
from solida.domain.entities.societaire import Societaire
from solida.domain.values.societaire_search_result import SocietaireSearchResult

STATUT_SOCIETAIRE_PAR_DEFAUT = "actif"
"""Le générateur ne modélise ni churn ni radiation : voir docs/backend/02-adapters-core-sim.md."""


class PostgresSocietaireReader:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def rechercher_societaires(
        self, terme: str, limite: int, agence_id: str | None = None
    ) -> list[SocietaireSearchResult]:
        query = text("""
            SELECT s.societaire_id, s.nom_complet, s.numero_membre, s.caisse_id, s.zone,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s
            WHERE (s.nom_complet ILIKE '%' || :terme || '%' OR s.numero_membre = :terme)
              AND (CAST(:agence_id AS text) IS NULL OR s.caisse_id = :agence_id)
            ORDER BY similarity(s.nom_complet, :terme) DESC
            LIMIT :limite
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(
                query, {"terme": terme, "limite": limite, "agence_id": agence_id}
            )
            return [
                SocietaireSearchResult(
                    societaire_id=row.societaire_id,
                    nom_complet=row.nom_complet,
                    numero_membre=row.numero_membre,
                    agence=row.caisse_id,
                    zone=row.zone,
                    statut=STATUT_SOCIETAIRE_PAR_DEFAUT,
                    a_credit_en_cours=bool(row.a_credit_en_cours),
                )
                for row in rows
            ]

    def compter_societaires(self, terme: str, agence_id: str | None = None) -> int:
        query = text("""
            SELECT count(*) FROM societaires s
            WHERE (s.nom_complet ILIKE '%' || :terme || '%' OR s.numero_membre = :terme)
              AND (CAST(:agence_id AS text) IS NULL OR s.caisse_id = :agence_id)
        """)
        with self._engine.connect() as connection:
            return connection.execute(query, {"terme": terme, "agence_id": agence_id}).scalar_one()

    def charger_societaire_par_numero_membre(self, numero_membre: str) -> Societaire | None:
        query = text("""
            SELECT s.societaire_id, s.numero_membre, s.nom_complet, s.caisse_id, s.date_adhesion,
                   s.anciennete_societaire_mois, s.segment, s.age, s.zone, s.nb_personnes_a_charge,
                   s.niveau_education, s.parts_sociales, s.revenu_declare, s.gie_id,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s WHERE s.numero_membre = :numero_membre
        """)
        with self._engine.connect() as connection:
            row = connection.execute(query, {"numero_membre": numero_membre}).first()
        if row is None:
            return None
        return Societaire(
            societaire_id=row.societaire_id,
            numero_membre=row.numero_membre,
            nom_complet=row.nom_complet,
            agence=row.caisse_id,
            date_adhesion=vers_date(row.date_adhesion),
            anciennete_mois=row.anciennete_societaire_mois,
            segment=row.segment,
            age=row.age,
            zone=row.zone,
            nb_personnes_a_charge=row.nb_personnes_a_charge,
            niveau_instruction=row.niveau_education,
            parts_sociales_montant=row.parts_sociales,
            revenu_mensuel_declare=(
                None if row.revenu_declare is None else round(row.revenu_declare)
            ),
            groupe_id=row.gie_id,
            a_credit_en_cours=bool(row.a_credit_en_cours),
        )

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        query = text("""
            SELECT s.societaire_id, s.numero_membre, s.nom_complet, s.caisse_id, s.date_adhesion,
                   s.anciennete_societaire_mois, s.segment, s.age, s.zone, s.nb_personnes_a_charge,
                   s.niveau_education, s.parts_sociales, s.revenu_declare, s.gie_id,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s WHERE s.societaire_id = :id
        """)
        with self._engine.connect() as connection:
            row = connection.execute(query, {"id": societaire_id}).first()
        if row is None:
            return None
        return Societaire(
            societaire_id=row.societaire_id,
            numero_membre=row.numero_membre,
            nom_complet=row.nom_complet,
            agence=row.caisse_id,
            date_adhesion=vers_date(row.date_adhesion),
            anciennete_mois=row.anciennete_societaire_mois,
            segment=row.segment,
            age=row.age,
            zone=row.zone,
            nb_personnes_a_charge=row.nb_personnes_a_charge,
            niveau_instruction=row.niveau_education,
            parts_sociales_montant=row.parts_sociales,
            revenu_mensuel_declare=(
                None if row.revenu_declare is None else round(row.revenu_declare)
            ),
            groupe_id=row.gie_id,
            a_credit_en_cours=bool(row.a_credit_en_cours),
        )
