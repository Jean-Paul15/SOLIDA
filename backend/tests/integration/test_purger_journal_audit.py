import os
import uuid
from datetime import UTC, datetime, timedelta

import pytest
import sqlalchemy as sa

from solida.batch.jobs.purger_journal_audit import RETENTION, purge
from solida.infrastructure.database import purge_audit_engine, solida_engine

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ,
    reason="Base reelle absente : integration non disponible ici",
)

_TYPE_TEST = "test_purge_journal_audit"


def _inserer(horodatage: datetime) -> uuid.UUID:
    evenement_id = uuid.uuid4()
    engine = solida_engine()
    with engine.connect() as connexion:
        connexion.execute(
            sa.text("""
                INSERT INTO journal_audit
                    (evenement_id, type, acteur_id, objet, details, horodatage)
                VALUES (:id, :type, 'test', 'test', '{}', :horodatage)
            """),
            {"id": evenement_id, "type": _TYPE_TEST, "horodatage": horodatage},
        )
        connexion.commit()
    return evenement_id


def _nettoyer() -> None:
    # journal_audit est en insertion seule (trigger journal_audit_insertion_seule) : seule une
    # connexion solida_purge avec le flag de session peut reellement supprimer une ligne.
    with purge_audit_engine().begin() as connexion:
        connexion.execute(sa.text("SET LOCAL solida.purge_audit = 'on'"))
        connexion.execute(
            sa.text("DELETE FROM journal_audit WHERE type = :type"), {"type": _TYPE_TEST}
        )


def test_purge_supprime_seulement_les_entrees_plus_vieilles_que_la_retention() -> None:
    maintenant = datetime.now(UTC)
    _inserer(maintenant - RETENTION - timedelta(days=1))  # au-dela : doit disparaitre
    _inserer(maintenant - timedelta(days=1))  # en-deca : doit rester
    try:
        with solida_engine().connect() as connexion:
            avant = connexion.execute(
                sa.text("SELECT count(*) FROM journal_audit WHERE type = :type"),
                {"type": _TYPE_TEST},
            ).scalar_one()
        assert avant == 2

        nb_supprimes = purge()

        with solida_engine().connect() as connexion:
            restantes = connexion.execute(
                sa.text("SELECT count(*) FROM journal_audit WHERE type = :type"),
                {"type": _TYPE_TEST},
            ).scalar_one()
        assert restantes == 1
        assert nb_supprimes >= 1
    finally:
        _nettoyer()


def test_essai_a_blanc_ne_supprime_rien() -> None:
    _inserer(datetime.now(UTC) - RETENTION - timedelta(days=1))
    try:
        nb_concernees = purge(dry_run=True)
        assert nb_concernees >= 1

        with solida_engine().connect() as connexion:
            restantes = connexion.execute(
                sa.text("SELECT count(*) FROM journal_audit WHERE type = :type"),
                {"type": _TYPE_TEST},
            ).scalar_one()
        assert restantes == 1
    finally:
        _nettoyer()
