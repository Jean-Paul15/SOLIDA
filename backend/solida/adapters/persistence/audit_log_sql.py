import uuid
from datetime import datetime

from sqlalchemy import JSON, Engine, bindparam, text


class SqlAuditLog:
    """Implémente `AuditLog` contre `journal_audit` (schéma `solida`)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def enregistrer_evenement(
        self,
        type_evenement: str,
        acteur_id: str,
        objet: str,
        details: dict[str, object],
        adresse_ip: str | None = None,
    ) -> None:
        # Les requêtes SQL brutes doivent fournir l'identifiant et le type JSON explicitement.
        statement = text("""
            INSERT INTO journal_audit (evenement_id, type, acteur_id, objet, details, adresse_ip)
            VALUES (:evenement_id, :type, :acteur_id, :objet, :details, :adresse_ip)
        """).bindparams(bindparam("details", type_=JSON))
        with self._engine.connect() as connection:
            connection.execute(
                statement,
                {
                    "evenement_id": uuid.uuid4(),
                    "type": type_evenement,
                    "acteur_id": acteur_id,
                    "objet": objet,
                    "details": details,
                    "adresse_ip": adresse_ip,
                },
            )
            connection.commit()

    def compter_evenements_recents(self, type_evenement: str, objet: str, depuis: datetime) -> int:
        statement = text("""
            SELECT count(*) FROM journal_audit
            WHERE type = :type AND objet = :objet AND horodatage >= :depuis
        """)
        with self._engine.connect() as connection:
            result = connection.execute(
                statement, {"type": type_evenement, "objet": objet, "depuis": depuis}
            )
            return int(result.scalar_one())

    def lister_objets_recents(self, type_evenement: str, acteur_id: str, limite: int) -> list[str]:
        """Renvoie les objets distincts récents pour alimenter les sociétaires récents."""
        statement = text("""
            SELECT objet, max(horodatage) AS dernier
            FROM journal_audit
            WHERE type = :type AND acteur_id = :acteur_id
            GROUP BY objet
            ORDER BY dernier DESC
            LIMIT :limite
        """)
        with self._engine.connect() as connection:
            result = connection.execute(
                statement, {"type": type_evenement, "acteur_id": acteur_id, "limite": limite}
            )
            return [row.objet for row in result]
