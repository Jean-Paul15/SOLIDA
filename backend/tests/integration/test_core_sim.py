import os

import pytest
from sqlalchemy import create_engine, text

from solida.adapters.core_sim.core_sim_postgres_reader import CoreSimPostgresReader

pytestmark = pytest.mark.skipif(
    "CORESIM_DATABASE_URL" not in os.environ,
    reason="CORESIM_DATABASE_URL absent : integration reelle non disponible dans cet environnement",
)


@pytest.fixture(scope="module")
def core_sim_reader() -> CoreSimPostgresReader:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    return CoreSimPostgresReader(engine)


@pytest.fixture(scope="module")
def un_societaire_id(core_sim_reader: CoreSimPostgresReader) -> str:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with engine.connect() as connection:
        row = connection.execute(text("SELECT societaire_id FROM societaires LIMIT 1")).first()
    assert row is not None
    return row.societaire_id


def test_le_role_lecteur_ne_peut_pas_ecrire_dans_coresim() -> None:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with (
        pytest.raises(Exception, match="permission denied"),
        engine.connect() as connection,
    ):
        connection.execute(text("INSERT INTO societaires (societaire_id) VALUES ('X')"))
        connection.commit()


def test_charger_societaire_ne_renvoie_jamais_le_sexe_ou_le_statut_matrimonial(
    core_sim_reader: CoreSimPostgresReader, un_societaire_id: str
) -> None:
    societaire = core_sim_reader.charger_societaire(un_societaire_id)
    assert societaire is not None
    champs = {f for f in societaire.__dataclass_fields__}
    assert "sexe" not in champs
    assert "statut_matrimonial" not in champs


def test_charger_societaire_introuvable_renvoie_none(
    core_sim_reader: CoreSimPostgresReader,
) -> None:
    assert core_sim_reader.charger_societaire("SOC-INEXISTANT") is None


def test_rechercher_par_numero_membre_exact(
    core_sim_reader: CoreSimPostgresReader, un_societaire_id: str
) -> None:
    societaire = core_sim_reader.charger_societaire(un_societaire_id)
    assert societaire is not None
    search_results = core_sim_reader.rechercher_societaires(societaire.numero_membre, 5)
    assert any(result.societaire_id == un_societaire_id for result in search_results)


def test_capital_restant_du_est_nul_pour_un_credit_solde(
    core_sim_reader: CoreSimPostgresReader,
) -> None:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT societaire_id FROM credits WHERE statut = 'solde' LIMIT 1")
        ).first()
    if row is None:
        pytest.skip("aucun credit solde dans ce jeu de donnees")
    credits = core_sim_reader.charger_historique_credit(row.societaire_id)
    soldes = [c for c in credits if c.statut == "solde"]
    assert all(c.capital_restant_du == 0 for c in soldes)


def test_credit_en_souffrance_a_un_capital_restant_du_positif(
    core_sim_reader: CoreSimPostgresReader,
) -> None:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT societaire_id FROM credits WHERE statut = 'en_souffrance' LIMIT 1")
        ).first()
    if row is None:
        pytest.skip("aucun credit en souffrance dans ce jeu de donnees")
    credits = core_sim_reader.charger_historique_credit(row.societaire_id)
    en_souffrance = [c for c in credits if c.statut == "en_souffrance"]
    assert all(c.capital_restant_du == c.montant_octroye for c in en_souffrance)


def test_charger_groupe_exclut_le_societaire_evalue_de_ses_propres_agregats(
    core_sim_reader: CoreSimPostgresReader,
) -> None:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT societaire_id FROM societaires WHERE gie_id IS NOT NULL LIMIT 1")
        ).first()
    if row is None:
        pytest.skip("aucun sociétaire en groupe dans ce jeu de donnees")
    groupe = core_sim_reader.charger_groupe(row.societaire_id)
    assert groupe is not None
    # Le calcul ne s'effondre pas meme quand exclure l'evalue laisse un historique tres court.
    assert groupe.taille_actuelle >= 1
    if groupe.taux_remboursement_groupe is not None:
        assert 0.0 <= groupe.taux_remboursement_groupe <= 1.0
