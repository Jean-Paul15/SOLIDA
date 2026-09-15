import uuid
from typing import Any

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

from solida.adapters.http.mappers.scoring import decision_a_enregistrer_to_resultat_scoring
from solida.domain.values.demande_societaire import (
    STATUT_ARCHIVEE,
    DemandeSocietaire,
    DemandeSocietaireACreer,
)


def _row_to_demande(row: Any) -> DemandeSocietaire:
    return DemandeSocietaire(
        demande_id=str(row.demande_id),
        societaire_id=row.societaire_id,
        agence_id=row.agence_id,
        montant_demande=row.montant_demande,
        objet_credit=row.objet_credit,
        duree_mois=row.duree_mois,
        produit_id=row.produit_id,
        resultat=row.resultat,
        statut=row.statut,
        cree_le=row.cree_le,
        assigne_a_agent_id=str(row.assigne_a_agent_id) if row.assigne_a_agent_id else None,
        archivee_le=row.archivee_le,
        archivee_par_agent_id=(
            str(row.archivee_par_agent_id) if row.archivee_par_agent_id else None
        ),
    )


class SqlDemandeSocietaireRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def enregistrer(self, demande: DemandeSocietaireACreer) -> DemandeSocietaire:
        query = text("""
            INSERT INTO demande_societaire
                (demande_id, societaire_id, agence_id, montant_demande, objet_credit,
                 duree_mois, produit_id, resultat, assigne_a_agent_id)
            VALUES
                (:demande_id, :societaire_id, :agence_id, :montant_demande, :objet_credit,
                 :duree_mois, :produit_id, :resultat, :assigne_a_agent_id)
            RETURNING *
        """).bindparams(bindparam("resultat", type_=JSONB))
        with self._engine.connect() as connection:
            row = connection.execute(
                query,
                {
                    "demande_id": uuid.UUID(demande.demande_id),
                    "societaire_id": demande.societaire_id,
                    "agence_id": demande.agence_id,
                    "montant_demande": demande.montant_demande,
                    "objet_credit": demande.objet_credit,
                    "duree_mois": demande.duree_mois,
                    "produit_id": demande.produit_id,
                    "resultat": decision_a_enregistrer_to_resultat_scoring(
                        demande.resultat
                    ).model_dump(mode="json"),
                    "assigne_a_agent_id": (
                        uuid.UUID(demande.assigne_a_agent_id)
                        if demande.assigne_a_agent_id
                        else None
                    ),
                },
            ).one()
            connection.commit()
        return _row_to_demande(row)

    def lister_non_assignees(
        self, agence_id: str | None, statut: str, limite: int, decalage: int
    ) -> list[DemandeSocietaire]:
        query = text("""
            SELECT * FROM demande_societaire
            WHERE (CAST(:agence_id AS text) IS NULL OR agence_id = :agence_id)
              AND statut = :statut
              AND assigne_a_agent_id IS NULL
            ORDER BY cree_le DESC
            LIMIT :limite OFFSET :decalage
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(
                query,
                {
                    "agence_id": agence_id,
                    "statut": statut,
                    "limite": limite,
                    "decalage": decalage,
                },
            )
            return [_row_to_demande(row) for row in rows]

    def compter_non_assignees(self, agence_id: str | None, statut: str) -> int:
        query = text("""
            SELECT count(*) FROM demande_societaire
            WHERE (CAST(:agence_id AS text) IS NULL OR agence_id = :agence_id)
              AND statut = :statut
              AND assigne_a_agent_id IS NULL
        """)
        with self._engine.connect() as connection:
            return connection.execute(
                query, {"agence_id": agence_id, "statut": statut}
            ).scalar_one()

    def lister_assignees(
        self, agence_id: str | None, agent_id: str, statut: str, limite: int, decalage: int
    ) -> list[DemandeSocietaire]:
        query = text("""
            SELECT * FROM demande_societaire
            WHERE (CAST(:agence_id AS text) IS NULL OR agence_id = :agence_id)
              AND statut = :statut
              AND assigne_a_agent_id = :agent_id
            ORDER BY cree_le DESC
            LIMIT :limite OFFSET :decalage
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(
                query,
                {
                    "agence_id": agence_id,
                    "agent_id": uuid.UUID(agent_id),
                    "statut": statut,
                    "limite": limite,
                    "decalage": decalage,
                },
            )
            return [_row_to_demande(row) for row in rows]

    def compter_assignees(self, agence_id: str | None, agent_id: str, statut: str) -> int:
        query = text("""
            SELECT count(*) FROM demande_societaire
            WHERE (CAST(:agence_id AS text) IS NULL OR agence_id = :agence_id)
              AND statut = :statut
              AND assigne_a_agent_id = :agent_id
        """)
        with self._engine.connect() as connection:
            return connection.execute(
                query,
                {"agence_id": agence_id, "agent_id": uuid.UUID(agent_id), "statut": statut},
            ).scalar_one()

    def lire(self, demande_id: str) -> DemandeSocietaire | None:
        query = text("SELECT * FROM demande_societaire WHERE demande_id = :id")
        with self._engine.connect() as connection:
            row = connection.execute(query, {"id": uuid.UUID(demande_id)}).first()
        return _row_to_demande(row) if row is not None else None

    def archiver(self, demande_id: str, agent_id: str) -> DemandeSocietaire | None:
        query = text("""
            UPDATE demande_societaire
            SET statut = :statut, archivee_le = now(), archivee_par_agent_id = :agent_id
            WHERE demande_id = :id
            RETURNING *
        """)
        with self._engine.connect() as connection:
            row = connection.execute(
                query,
                {
                    "statut": STATUT_ARCHIVEE,
                    "agent_id": uuid.UUID(agent_id),
                    "id": uuid.UUID(demande_id),
                },
            ).first()
            connection.commit()
        return _row_to_demande(row) if row is not None else None

    def assigner(self, demande_id: str, agent_id: str) -> DemandeSocietaire | None:
        query = text("""
            UPDATE demande_societaire
            SET assigne_a_agent_id = :agent_id
            WHERE demande_id = :id
            RETURNING *
        """)
        with self._engine.connect() as connection:
            row = connection.execute(
                query, {"agent_id": uuid.UUID(agent_id), "id": uuid.UUID(demande_id)}
            ).first()
            connection.commit()
        return _row_to_demande(row) if row is not None else None
