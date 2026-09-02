import uuid
from datetime import datetime

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

from solida.adapters.persistence.decision_sql_mapper import (
    decomposition_to_json,
    result_complement_to_json,
    row_to_decision,
)
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree


class SqlDecisionRepository:
    """Implémente `DecisionRepository` contre `decision_scoring` (schéma `solida`).

    N'exécute jamais d'UPDATE ni de DELETE sur cette table : le déclencheur
    `decision_scoring_insertion_seule` en base le refuserait de toute façon,
    mais ce dépôt n'essaie même pas.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def enregistrer(self, decision: DecisionAEnregistrer) -> DecisionEnregistree:
        # Un retry identique renvoie la décision récente au lieu de créer un doublon.
        duplicate_query = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE d.societaire_id = :societaire_id AND d.agent_id = :agent_id
              AND d.entree = :entree AND d.horodatage > now() - interval '10 seconds'
            ORDER BY d.horodatage DESC LIMIT 1
        """).bindparams(bindparam("entree", type_=JSONB))

        # psycopg3 exige un type JSONB explicite pour sérialiser les dictionnaires Python.
        insert_statement = text("""
            INSERT INTO decision_scoring
                (decision_id, societaire_id, agent_id, entree, features_utilisees,
                 probabilite, score, tranche, montant_recommande, mode_calcul,
                 decomposition, resultat_complementaire, version_modele, version_grille)
            VALUES
                (:decision_id, :societaire_id, :agent_id, :entree, :features_utilisees,
                 :probabilite, :score, :tranche, :montant_recommande, :mode_calcul,
                 :decomposition, :resultat_complementaire, :version_modele, :version_grille)
            RETURNING *
        """).bindparams(
            bindparam("entree", type_=JSONB),
            bindparam("features_utilisees", type_=JSONB),
            bindparam("decomposition", type_=JSONB),
            bindparam("resultat_complementaire", type_=JSONB),
        )
        with self._engine.connect() as connection:
            duplicate_row = connection.execute(
                duplicate_query,
                {
                    "societaire_id": decision.societaire_id,
                    "agent_id": uuid.UUID(decision.agent_id),
                    "entree": decision.entree,
                },
            ).first()
            if duplicate_row is not None:
                return row_to_decision(
                    duplicate_row, duplicate_row.agent_nom, duplicate_row.agent_agence_id
                )

            row = connection.execute(
                insert_statement,
                {
                    "decision_id": uuid.UUID(decision.decision_id),
                    "societaire_id": decision.societaire_id,
                    "agent_id": uuid.UUID(decision.agent_id),
                    "entree": decision.entree,
                    "features_utilisees": decision.features_utilisees,
                    "probabilite": decision.probabilite,
                    "score": decision.score.valeur,
                    "tranche": decision.tranche.value,
                    "montant_recommande": decision.montant_recommande.valeur,
                    "mode_calcul": decision.mode_calcul.value,
                    "decomposition": decomposition_to_json(decision.decomposition),
                    "resultat_complementaire": result_complement_to_json(decision),
                    "version_modele": decision.version_modele,
                    "version_grille": decision.version_grille,
                },
            ).one()
            connection.commit()

        return row_to_decision(row, decision.agent_nom, decision.agent_agence_id)

    def lire(self, decision_id: str) -> DecisionEnregistree | None:
        query = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE d.decision_id = :id
        """)
        with self._engine.connect() as connection:
            row = connection.execute(query, {"id": uuid.UUID(decision_id)}).first()
        if row is None:
            return None
        return row_to_decision(row, row.agent_nom, row.agent_agence_id)

    def lister(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> list[DecisionEnregistree]:
        query = text("""
            SELECT d.*, u.nom_complet AS agent_nom, u.agence_id AS agent_agence_id
            FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE CAST(:agence_id AS text) IS NULL OR u.agence_id = :agence_id
            ORDER BY d.horodatage DESC
            LIMIT :limite OFFSET :decalage
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(
                query, {"agence_id": agence_id, "limite": limite, "decalage": decalage}
            )
            return [row_to_decision(row, row.agent_nom, row.agent_agence_id) for row in rows]

    def compter(self, agence_id: str | None) -> int:
        query = text("""
            SELECT count(*) FROM decision_scoring d
            JOIN utilisateur u ON u.id = d.agent_id
            WHERE CAST(:agence_id AS text) IS NULL OR u.agence_id = :agence_id
        """)
        with self._engine.connect() as connection:
            return connection.execute(query, {"agence_id": agence_id}).scalar_one()

    def existe_decision_accordee_depuis(
        self, societaire_id: str, depuis: datetime, entree_actuelle: dict[str, object]
    ) -> bool:
        # Exclut le retry identique, déjà couvert par la déduplication à l'écriture.
        query = text("""
            SELECT 1 FROM decision_scoring
            WHERE societaire_id = :societaire_id
              AND tranche IN ('accord', 'accord_sous_condition')
              AND horodatage >= :depuis
              AND entree IS DISTINCT FROM :entree_actuelle
            LIMIT 1
        """).bindparams(bindparam("entree_actuelle", type_=JSONB))
        with self._engine.connect() as connection:
            return (
                connection.execute(
                    query,
                    {
                        "societaire_id": societaire_id,
                        "depuis": depuis,
                        "entree_actuelle": entree_actuelle,
                    },
                ).first()
                is not None
            )
