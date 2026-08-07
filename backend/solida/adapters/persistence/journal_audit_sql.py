import uuid
from datetime import datetime

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
        adresse_ip: str | None = None,
    ) -> None:
        # evenement_id genere ici : la colonne n'a pas de server_default, seulement un
        # defaut cote ORM (jamais applique par cette instruction SQL brute). bindparams
        # (type_=JSON) : psycopg3 n'adapte pas un dict Python tout seul.
        instruction = text("""
            INSERT INTO journal_audit (evenement_id, type, acteur_id, objet, details, adresse_ip)
            VALUES (:evenement_id, :type, :acteur_id, :objet, :details, :adresse_ip)
        """).bindparams(bindparam("details", type_=JSON))
        with self._moteur.connect() as connexion:
            connexion.execute(
                instruction,
                {
                    "evenement_id": uuid.uuid4(),
                    "type": type_evenement,
                    "acteur_id": acteur_id,
                    "objet": objet,
                    "details": details,
                    "adresse_ip": adresse_ip,
                },
            )
            connexion.commit()

    def compter_evenements_recents(
        self, type_evenement: str, objet: str, depuis: datetime
    ) -> int:
        instruction = text("""
            SELECT count(*) FROM journal_audit
            WHERE type = :type AND objet = :objet AND horodatage >= :depuis
        """)
        with self._moteur.connect() as connexion:
            resultat = connexion.execute(
                instruction, {"type": type_evenement, "objet": objet, "depuis": depuis}
            )
            return int(resultat.scalar_one())

    def lister_objets_recents(
        self, type_evenement: str, acteur_id: str, limite: int
    ) -> list[str]:
        """`objet` distincts les plus récemment journalisés pour cet acteur, du plus
        récent au plus ancien — sert les "sociétaires récents" de l'agent connecté."""
        instruction = text("""
            SELECT objet, max(horodatage) AS dernier
            FROM journal_audit
            WHERE type = :type AND acteur_id = :acteur_id
            GROUP BY objet
            ORDER BY dernier DESC
            LIMIT :limite
        """)
        with self._moteur.connect() as connexion:
            resultat = connexion.execute(
                instruction, {"type": type_evenement, "acteur_id": acteur_id, "limite": limite}
            )
            return [ligne.objet for ligne in resultat]
