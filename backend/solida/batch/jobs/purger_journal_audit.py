"""Purge du journal d'audit au-delà de sa durée de rétention.

RÉTENTION : 1 an. La loi togolaise n°2019-014 sur la protection des données à caractère
personnel impose un droit à l'effacement « quand la conservation n'est plus justifiée »,
sans fixer de durée précise pour un journal de sécurité. En l'absence d'un mandat
sectoriel togolais/UEMOA plus précis, 1 an est la durée par défaut vers laquelle
convergent PCI-DSS, FISMA, HIPAA, SOX et GLBA pour ce type de journal — voir
`docs/backend/03-decisions-provisoires-a-revoir.md` pour le détail de cet arbitrage et
la source des chiffres.

Aucun ordonnanceur n'existe dans la pile SOLIDA (pas de conteneur cron) : ce script
s'exécute manuellement ou via une tâche planifiée externe (cron de l'hôte), pas tout
seul. À planifier en production, par exemple une fois par jour :

  0 3 * * * docker compose run --rm api python -m solida.batch.jobs.purger_journal_audit

Usage :
  docker compose run --rm api python -m solida.batch.jobs.purger_journal_audit
  docker compose run --rm api python -m solida.batch.jobs.purger_journal_audit --essai-a-blanc
"""

import argparse
import logging
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa

from solida.infrastructure.database import moteur_solida

logger = logging.getLogger(__name__)

RETENTION = timedelta(days=365)


def purger(essai_a_blanc: bool = False) -> int:
    """Supprime les entrées de `journal_audit` plus vieilles que `RETENTION`.

    Renvoie le nombre de lignes supprimées — ou, en essai à blanc, le nombre de lignes
    qui l'auraient été, sans rien supprimer.
    """
    seuil = datetime.now(UTC) - RETENTION
    moteur = moteur_solida()

    if essai_a_blanc:
        instruction = sa.text("SELECT count(*) FROM journal_audit WHERE horodatage < :seuil")
        with moteur.connect() as connexion:
            return int(connexion.execute(instruction, {"seuil": seuil}).scalar_one())

    instruction = sa.text("DELETE FROM journal_audit WHERE horodatage < :seuil")
    with moteur.connect() as connexion:
        resultat = connexion.execute(instruction, {"seuil": seuil})
        connexion.commit()
        return resultat.rowcount


def _principal() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--essai-a-blanc",
        action="store_true",
        help="Compte les entrées concernées sans les supprimer.",
    )
    arguments = analyseur.parse_args()
    logging.basicConfig(level=logging.INFO)
    nb = purger(arguments.essai_a_blanc)
    verbe = "seraient supprimées" if arguments.essai_a_blanc else "supprimées"
    logger.info("%d entrée(s) du journal d'audit %s (rétention : %s).", nb, verbe, RETENTION)


if __name__ == "__main__":
    _principal()
