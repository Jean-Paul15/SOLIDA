"""Purge les journaux d'audit âgés de plus d'un an.

Le rôle dédié `solida_purge` est requis car le journal est en insertion seule. La durée et
l'exécution planifiée externe sont documentées dans les décisions backend.
"""

import argparse
import logging
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from solida.infrastructure.database import purge_audit_engine, solida_engine

logger = logging.getLogger(__name__)

RETENTION = timedelta(days=365)


def purge(dry_run: bool = False) -> int:
    """Supprime les journaux expirés, ou les compte sans écriture en essai à blanc."""
    threshold = datetime.now(UTC) - RETENTION

    if dry_run:
        statement = sa.text("SELECT count(*) FROM journal_audit WHERE horodatage < :seuil")
        with solida_engine().connect() as connection:
            return int(connection.execute(statement, {"seuil": threshold}).scalar_one())

    statement = sa.text("DELETE FROM journal_audit WHERE horodatage < :seuil")
    with purge_audit_engine().begin() as connection:
        connection.execute(sa.text("SET LOCAL solida.purge_audit = 'on'"))
        result = connection.execute(statement, {"seuil": threshold})
        return result.rowcount


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--essai-a-blanc",
        action="store_true",
        help="Compte les entrées concernées sans les supprimer.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    count = purge(args.essai_a_blanc)
    verb = "seraient supprimées" if args.essai_a_blanc else "supprimées"
    logger.info("%d entrée(s) du journal d'audit %s (rétention : %s).", count, verb, RETENTION)


if __name__ == "__main__":
    _main()
