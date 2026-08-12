import os
import uuid

import pytest
import sqlalchemy as sa

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ,
    reason="Base reelle absente : integration non disponible ici",
)


def _inserer_evenement_test(connexion: sa.Connection) -> uuid.UUID:
    evenement_id = uuid.uuid4()
    connexion.execute(
        sa.text("""
            INSERT INTO journal_audit (evenement_id, type, acteur_id, objet, details)
            VALUES (:id, 'test_immuabilite', 'test', 'test', '{}')
        """),
        {"id": evenement_id},
    )
    return evenement_id


def test_solida_app_ne_peut_ni_modifier_ni_supprimer_journal_audit() -> None:
    # journal_audit est en insertion seule (trigger journal_audit_insertion_seule) : meme le
    # role applicatif normal, proprietaire de la table, ne peut pas alterer une ligne existante.
    moteur = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.connect() as connexion:
        evenement_id = _inserer_evenement_test(connexion)
        connexion.commit()

    with moteur.connect() as connexion:
        with pytest.raises(sa.exc.DBAPIError, match="insertion seule"):
            connexion.execute(
                sa.text("UPDATE journal_audit SET objet = 'modifie' WHERE evenement_id = :id"),
                {"id": evenement_id},
            )
        connexion.rollback()

    with moteur.connect() as connexion:
        with pytest.raises(sa.exc.DBAPIError, match="insertion seule"):
            connexion.execute(
                sa.text("DELETE FROM journal_audit WHERE evenement_id = :id"), {"id": evenement_id}
            )
        connexion.rollback()


def test_solida_purge_sans_le_flag_de_session_ne_peut_pas_supprimer() -> None:
    # Le role dedie a la purge est bloque comme n'importe qui d'autre tant que le flag de
    # session attendu par le trigger n'est pas explicitement pose.
    if "SOLIDA_PURGE_DATABASE_URL" not in os.environ:
        pytest.skip("SOLIDA_PURGE_DATABASE_URL absent : role de purge non disponible ici")

    moteur_app = sa.create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur_app.connect() as connexion:
        evenement_id = _inserer_evenement_test(connexion)
        connexion.commit()

    moteur_purge = sa.create_engine(os.environ["SOLIDA_PURGE_DATABASE_URL"])
    with moteur_purge.connect() as connexion:
        with pytest.raises(sa.exc.DBAPIError, match="insertion seule"):
            connexion.execute(
                sa.text("DELETE FROM journal_audit WHERE evenement_id = :id"), {"id": evenement_id}
            )
        connexion.rollback()

    # Nettoyage via le chemin legitime (flag pose), pour ne pas polluer les executions suivantes.
    with moteur_purge.begin() as connexion:
        connexion.execute(sa.text("SET LOCAL solida.purge_audit = 'on'"))
        connexion.execute(
            sa.text("DELETE FROM journal_audit WHERE evenement_id = :id"), {"id": evenement_id}
        )
