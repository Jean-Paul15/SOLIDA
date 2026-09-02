import uuid

from sqlalchemy import Engine, text


class SqlFicheArchiveeRepository:
    """Implémente `FicheArchiveeRepository` contre `fiche_archivee` (schéma `solida`)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def enregistrer(self, decision_id: str, chemin_objet: str, archive_par: str) -> str:
        fiche_id = str(uuid.uuid4())
        statement = text("""
            INSERT INTO fiche_archivee (fiche_id, decision_id, chemin_objet, archive_par)
            VALUES (:fiche_id, :decision_id, :chemin_objet, :archive_par)
        """)
        with self._engine.connect() as connection:
            connection.execute(
                statement,
                {
                    "fiche_id": fiche_id,
                    "decision_id": decision_id,
                    "chemin_objet": chemin_objet,
                    "archive_par": archive_par,
                },
            )
            connection.commit()
        return fiche_id
