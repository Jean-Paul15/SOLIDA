import logging
import sys


def configurer_journalisation() -> None:
    """Journalisation applicative sur stdout — capturée par `docker logs`, pas de service
    externe : cohérent avec la contrainte de légèreté du projet. Le journal d'audit métier
    (`journal_audit`, en base) est distinct et complémentaire, pas remplacé par ceci."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )
