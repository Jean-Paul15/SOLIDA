"""Alerte les pics de lecture sans bloquer automatiquement les comptes.

Le seuil vient du pentest et reste ajustable dans la documentation de sécurité.
L'ordonnancement relève d'une tâche externe.
"""

import argparse
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.infrastructure.database import solida_engine

logger = logging.getLogger(__name__)

FENETRE = timedelta(hours=1)
SEUIL_LECTURES = 100

TYPES_LECTURE = ("recherche_societaires", "consultation_dossier")


@dataclass(frozen=True)
class AlertedActor:
    acteur_id: str
    nombre_lectures: int


def detect(since: datetime | None = None) -> list[AlertedActor]:
    """Renvoie les acteurs au-dessus du seuil, sans écrire."""
    time_threshold = since or (datetime.now(UTC) - FENETRE)
    statement = sa.text("""
        SELECT acteur_id, count(*) AS nb
        FROM journal_audit
        WHERE type = ANY(:types) AND horodatage >= :depuis
        GROUP BY acteur_id
        HAVING count(*) > :seuil
        ORDER BY nb DESC
    """)
    with solida_engine().connect() as connection:
        rows = connection.execute(
            statement,
            {"types": list(TYPES_LECTURE), "depuis": time_threshold, "seuil": SEUIL_LECTURES},
        )
        return [AlertedActor(acteur_id=row.acteur_id, nombre_lectures=row.nb) for row in rows]


def alert(dry_run: bool = False) -> list[AlertedActor]:
    """Journalise les alertes sauf en essai à blanc ; ne bloque jamais de compte."""
    exceeded_actors = detect()
    if dry_run or not exceeded_actors:
        return exceeded_actors

    audit_log = SqlAuditLog(solida_engine())
    for actor in exceeded_actors:
        audit_log.enregistrer_evenement(
            "alerte_volume_lecture",
            actor.acteur_id,
            actor.acteur_id,
            {
                "nombre_lectures": actor.nombre_lectures,
                "fenetre_heures": FENETRE.total_seconds() / 3600,
                "seuil": SEUIL_LECTURES,
            },
        )
    return exceeded_actors


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--essai-a-blanc",
        action="store_true",
        help="Detecte et affiche sans ecrire d'alerte dans journal_audit.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    exceeded_actors = alert(args.essai_a_blanc)
    if not exceeded_actors:
        logger.info("Aucun acteur au-dessus du seuil (%d lectures/%s).", SEUIL_LECTURES, FENETRE)
        return
    for actor in exceeded_actors:
        logger.warning(
            "acteur=%s nombre_lectures=%d (seuil=%d, fenetre=%s)%s",
            actor.acteur_id,
            actor.nombre_lectures,
            SEUIL_LECTURES,
            FENETRE,
            " [essai a blanc, rien ecrit]" if args.essai_a_blanc else "",
        )


if __name__ == "__main__":
    _main()
