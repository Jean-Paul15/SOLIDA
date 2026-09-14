import uuid
from typing import Any

from sqlalchemy import Engine, text

from solida.domain.values.utilisateur import UtilisateurResume


def _row_to_utilisateur(row: Any) -> UtilisateurResume:
    return UtilisateurResume(
        id=str(row.id),
        nom_complet=row.nom_complet,
        role=row.role,
        agence_id=row.agence_id,
        desactive_le=row.desactive_le,
    )


class SqlUtilisateurRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def lire(self, utilisateur_id: str) -> UtilisateurResume | None:
        query = text("""
            SELECT id, nom_complet, role, agence_id, desactive_le
            FROM utilisateur
            WHERE id = :id
        """)
        try:
            id_ = uuid.UUID(utilisateur_id)
        except ValueError:
            return None
        with self._engine.connect() as connection:
            row = connection.execute(query, {"id": id_}).first()
        return _row_to_utilisateur(row) if row is not None else None

    def lister_agents_agence(self, agence_id: str) -> list[UtilisateurResume]:
        query = text("""
            SELECT id, nom_complet, role, agence_id, desactive_le
            FROM utilisateur
            WHERE role = 'agent' AND agence_id = :agence_id AND desactive_le IS NULL
            ORDER BY nom_complet
        """)
        with self._engine.connect() as connection:
            rows = connection.execute(query, {"agence_id": agence_id})
            return [_row_to_utilisateur(row) for row in rows]
