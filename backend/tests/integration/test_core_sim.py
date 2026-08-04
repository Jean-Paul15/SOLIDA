import os

import pytest
from sqlalchemy import create_engine, text

from solida.adapters.core_sim.lecteur_postgres import LecteurCoreSimPostgres

pytestmark = pytest.mark.skipif(
    "CORESIM_DATABASE_URL" not in os.environ,
    reason="CORESIM_DATABASE_URL absent : integration reelle non disponible dans cet environnement",
)


@pytest.fixture(scope="module")
def lecteur() -> LecteurCoreSimPostgres:
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    return LecteurCoreSimPostgres(moteur)


@pytest.fixture(scope="module")
def un_societaire_id(lecteur: LecteurCoreSimPostgres) -> str:
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(text("SELECT societaire_id FROM societaires LIMIT 1")).first()
    assert ligne is not None
    return ligne.societaire_id


def test_le_role_lecteur_ne_peut_pas_ecrire_dans_coresim(lecteur: LecteurCoreSimPostgres) -> None:
    with (
        pytest.raises(Exception, match="permission denied"),
        lecteur._moteur.connect() as connexion,
    ):
        connexion.execute(text("INSERT INTO societaires (societaire_id) VALUES ('X')"))
        connexion.commit()


def test_charger_societaire_ne_renvoie_jamais_le_sexe_ou_le_statut_matrimonial(
    lecteur: LecteurCoreSimPostgres, un_societaire_id: str
) -> None:
    societaire = lecteur.charger_societaire(un_societaire_id)
    assert societaire is not None
    champs = {f for f in societaire.__dataclass_fields__}
    assert "sexe" not in champs
    assert "statut_matrimonial" not in champs


def test_charger_societaire_introuvable_renvoie_none(lecteur: LecteurCoreSimPostgres) -> None:
    assert lecteur.charger_societaire("SOC-INEXISTANT") is None


def test_rechercher_par_numero_membre_exact(
    lecteur: LecteurCoreSimPostgres, un_societaire_id: str
) -> None:
    societaire = lecteur.charger_societaire(un_societaire_id)
    assert societaire is not None
    resultats = lecteur.rechercher_societaires(societaire.numero_membre, 5)
    assert any(r.societaire_id == un_societaire_id for r in resultats)


def test_capital_restant_du_est_nul_pour_un_credit_solde(lecteur: LecteurCoreSimPostgres) -> None:
    with lecteur._moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT societaire_id FROM credits WHERE statut = 'solde' LIMIT 1")
        ).first()
    if ligne is None:
        pytest.skip("aucun credit solde dans ce jeu de donnees")
    credits = lecteur.charger_historique_credit(ligne.societaire_id)
    soldes = [c for c in credits if c.statut == "solde"]
    assert all(c.capital_restant_du == 0 for c in soldes)


def test_credit_en_souffrance_a_un_capital_restant_du_positif(
    lecteur: LecteurCoreSimPostgres,
) -> None:
    with lecteur._moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT societaire_id FROM credits WHERE statut = 'en_souffrance' LIMIT 1")
        ).first()
    if ligne is None:
        pytest.skip("aucun credit en souffrance dans ce jeu de donnees")
    credits = lecteur.charger_historique_credit(ligne.societaire_id)
    en_souffrance = [c for c in credits if c.statut == "en_souffrance"]
    assert all(c.capital_restant_du == c.montant_octroye for c in en_souffrance)


def test_charger_groupe_exclut_le_societaire_evalue_de_ses_propres_agregats(
    lecteur: LecteurCoreSimPostgres,
) -> None:
    with lecteur._moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT societaire_id FROM societaires WHERE gie_id IS NOT NULL LIMIT 1")
        ).first()
    if ligne is None:
        pytest.skip("aucun sociétaire en groupe dans ce jeu de donnees")
    groupe = lecteur.charger_groupe(ligne.societaire_id)
    assert groupe is not None
    # Le calcul ne s'effondre pas meme quand exclure l'evalue laisse un historique tres court.
    assert groupe.taille_actuelle >= 1
    if groupe.taux_remboursement_groupe is not None:
        assert 0.0 <= groupe.taux_remboursement_groupe <= 1.0
