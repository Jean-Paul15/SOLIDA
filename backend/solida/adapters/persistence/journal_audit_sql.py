from sqlalchemy import JSON, Engine, bindparam, text


class JournalAuditSql:
    """Implémente `JournalAudit` contre `journal_audit` (schéma `solida`)."""

    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def enregistrer_evenement(
        self,
        type_evenement: str,
        acteur_id: str,
        objet: str,
        details: dict[str, object],
    ) -> None:
        # bindparams(type_=JSON) : psycopg3 n'adapte pas un dict Python tout seul.
        instruction = text("""
            INSERT INTO journal_audit (type, acteur_id, objet, details)
            VALUES (:type, :acteur_id, :objet, :details)
        """).bindparams(bindparam("details", type_=JSON))
        with self._moteur.connect() as connexion:
            connexion.execute(
                instruction,
                {
                    "type": type_evenement,
                    "acteur_id": acteur_id,
                    "objet": objet,
                    "details": details,
                },
            )
            connexion.commit()
