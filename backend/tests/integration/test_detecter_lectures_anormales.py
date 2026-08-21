import os
import uuid

import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ,
    reason="Base reelle absente : integration non disponible ici",
)


def _generer_lectures(connexion: sa.Connection, acteur_id: str, nombre: int) -> None:
    connexion.execute(
        sa.text("""
            INSERT INTO journal_audit (evenement_id, type, acteur_id, objet, details, horodatage)
            SELECT gen_random_uuid(), 'recherche_societaires', :acteur_id, 'terme', '{}', now()
            FROM generate_series(1, :nombre)
        """),
        {"acteur_id": acteur_id, "nombre": nombre},
    )


def test_detecter_signale_un_acteur_au_dessus_du_seuil() -> None:
    from solida.batch.jobs.detecter_lectures_anormales import SEUIL_LECTURES, detect

    acteur_id = f"test-volume-{uuid.uuid4().hex[:8]}"
    moteur = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.begin() as connexion:
        _generer_lectures(connexion, acteur_id, SEUIL_LECTURES + 1)

    resultats = {a.acteur_id: a.nombre_lectures for a in detect()}
    assert acteur_id in resultats
    assert resultats[acteur_id] == SEUIL_LECTURES + 1


def test_detecter_ne_signale_pas_un_acteur_sous_le_seuil() -> None:
    from solida.batch.jobs.detecter_lectures_anormales import SEUIL_LECTURES, detect

    acteur_id = f"test-volume-{uuid.uuid4().hex[:8]}"
    moteur = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.begin() as connexion:
        _generer_lectures(connexion, acteur_id, SEUIL_LECTURES)

    resultats = {a.acteur_id for a in detect()}
    assert acteur_id not in resultats


def test_alerter_ecrit_une_entree_journal_audit_sans_toucher_au_compte() -> None:
    from solida.batch.jobs.detecter_lectures_anormales import SEUIL_LECTURES, alert

    acteur_id = f"test-volume-{uuid.uuid4().hex[:8]}"
    moteur = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.begin() as connexion:
        _generer_lectures(connexion, acteur_id, SEUIL_LECTURES + 1)

    depasses = alert()
    assert any(a.acteur_id == acteur_id for a in depasses)

    with moteur.connect() as connexion:
        alerte = connexion.execute(
            sa.text("""
                SELECT type, details FROM journal_audit
                WHERE type = 'alerte_volume_lecture' AND acteur_id = :acteur_id
            """),
            {"acteur_id": acteur_id},
        ).first()
    assert alerte is not None
    assert alerte.details["nombre_lectures"] == SEUIL_LECTURES + 1


def test_alerter_essai_a_blanc_necrit_rien() -> None:
    from solida.batch.jobs.detecter_lectures_anormales import SEUIL_LECTURES, alert

    acteur_id = f"test-volume-{uuid.uuid4().hex[:8]}"
    moteur = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.begin() as connexion:
        _generer_lectures(connexion, acteur_id, SEUIL_LECTURES + 1)

    alert(essai_a_blanc=True)

    with moteur.connect() as connexion:
        alerte = connexion.execute(
            sa.text("""
                SELECT 1 FROM journal_audit
                WHERE type = 'alerte_volume_lecture' AND acteur_id = :acteur_id
            """),
            {"acteur_id": acteur_id},
        ).first()
    assert alerte is None
