import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from solida.infrastructure.application_fastapi import app

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ or "CORESIM_DATABASE_URL" not in os.environ,
    reason="Bases reelles absentes : integration non disponible ici",
)


@pytest.fixture
def client_agent() -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/login",
        json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"},
    )
    return client


@pytest.fixture
def client_auditeur() -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/login",
        json={"identifiant": "auditeur.interne", "mot_de_passe": "solida-demo"},
    )
    return client


@pytest.fixture
def client_superviseur() -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/login",
        json={"identifiant": "superviseur.reseau", "mot_de_passe": "solida-demo"},
    )
    return client


@pytest.fixture
def societaire_agence_agent() -> str:
    # Un societaire distinct par test (pas `scope="module"` partage) : plusieurs tests de ce
    # module confirment un octroi "accord" sur ce fixture, et le controle multi-octroi
    # (finding 12, round 3 du pentest) bloquerait alors tous les tests suivants du module qui
    # reutiliseraient le meme societaire, meme sans rapport avec ce qu'ils testent.
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("""
                SELECT s.societaire_id FROM societaires s
                WHERE s.caisse_id = 'CAI-00' AND NOT EXISTS (
                    SELECT 1 FROM credits c
                    WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                )
                ORDER BY random() LIMIT 1
            """)
        ).first()
    assert ligne is not None
    return ligne.societaire_id


@pytest.fixture(scope="module")
def societaire_avec_credit_en_cours() -> str:
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("""
                SELECT s.societaire_id FROM societaires s
                JOIN credits c ON c.societaire_id = s.societaire_id
                WHERE s.caisse_id = 'CAI-00' AND c.statut = 'en_cours'
                LIMIT 1
            """)
        ).first()
    if ligne is None:
        pytest.skip("Aucun societaire CAI-00 avec un credit en cours dans ce jeu de donnees")
    return ligne.societaire_id


@pytest.fixture(scope="module")
def societaire_autre_agence() -> str:
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT societaire_id FROM societaires WHERE caisse_id != 'CAI-00' LIMIT 1")
        ).first()
    assert ligne is not None
    return ligne.societaire_id


def _demande(societaire_id: str) -> dict[str, object]:
    return {
        "societaire_id": societaire_id,
        "produit_id": "prod-individuel",
        "montant_demande": 100000,
        "duree_demandee_mois": 6,
        "objet_credit": "stock",
    }


def test_previsualiser_ne_persiste_rien(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    moteur = create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.connect() as connexion:
        avant = connexion.execute(text("SELECT count(*) FROM decision_scoring")).scalar_one()

    reponse = client_agent.post("/api/v1/scoring/preview", json=_demande(societaire_agence_agent))
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["montant_demande"] == 100000
    assert resultat["tranche"] in {"accord", "accord_sous_condition", "comite_de_credit", "refus"}
    # ConstantScoringModel renvoie une probabilité fixe (les features ne l'influencent pas) mais
    # produit une décomposition heuristique (pas apprise) pour que la fiche de justification
    # ne soit pas vide en attendant le vrai modèle (voir modele_constant.py et
    # docs/backend/03-decisions-provisoires-a-revoir.md).
    assert len(resultat["decomposition"]) > 0
    premiere = resultat["decomposition"][0]
    assert premiere.keys() >= {"code_variable", "libelle", "valeur", "points", "sens", "famille"}

    with moteur.connect() as connexion:
        apres = connexion.execute(text("SELECT count(*) FROM decision_scoring")).scalar_one()
    assert apres == avant


def test_confirmer_puis_relire_la_decision(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_agence_agent)
    )
    assert reponse_scoring.status_code == 201
    resultat = reponse_scoring.json()
    assert resultat["montant_demande"] == 100000
    assert "Score calculé avec un modèle de substitution" in resultat["avertissements"][0]

    decision_id = resultat["decision_id"]
    reponse_lecture = client_agent.get(f"/api/v1/scoring/{decision_id}")
    assert reponse_lecture.status_code == 200
    assert reponse_lecture.json() == resultat

    reponse_fiche = client_agent.get(f"/api/v1/scoring/{decision_id}/fiche")
    assert reponse_fiche.status_code == 200
    assert reponse_fiche.json()["fiche_id"] == decision_id


def test_confirmations_dupliquees_renvoient_la_meme_decision(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    # Deux confirmations identiques (double-clic, retry reseau) dans une fenetre courte ne
    # doivent pas persister deux decisions distinctes.
    demande = _demande(societaire_agence_agent)
    demande["objet_credit"] = "urgence_sante"  # objet distinct des autres tests de ce module

    premiere = client_agent.post("/api/v1/scoring/confirm", json=demande)
    assert premiere.status_code == 201
    deuxieme = client_agent.post("/api/v1/scoring/confirm", json=demande)
    assert deuxieme.status_code == 201

    assert premiere.json()["decision_id"] == deuxieme.json()["decision_id"]


def test_confirmer_un_societaire_introuvable_renvoie_404(client_agent: TestClient) -> None:
    reponse = client_agent.post("/api/v1/scoring/confirm", json=_demande("SOC-INEXISTANT"))
    assert reponse.status_code == 404


def test_montant_au_dela_du_plafond_institutionnel_est_rejete(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    moteur = create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.connect() as connexion:
        avant = connexion.execute(text("SELECT count(*) FROM decision_scoring")).scalar_one()

    demande = _demande(societaire_agence_agent)
    demande["montant_demande"] = 100_000_001
    reponse = client_agent.post("/api/v1/scoring/preview", json=demande)
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "montant_invalide"

    with moteur.connect() as connexion:
        apres = connexion.execute(text("SELECT count(*) FROM decision_scoring")).scalar_one()
    assert apres == avant


def test_produit_inconnu_renvoie_404(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    demande = _demande(societaire_agence_agent)
    demande["produit_id"] = "prod-inexistant"
    reponse = client_agent.post("/api/v1/scoring/preview", json=demande)
    assert reponse.status_code == 404
    assert reponse.json()["code"] == "introuvable"


def test_auditeur_ne_peut_pas_scorer(
    client_auditeur: TestClient, societaire_agence_agent: str
) -> None:
    reponse = client_auditeur.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_agence_agent)
    )
    assert reponse.status_code == 403


def test_agent_ne_peut_pas_scorer_hors_de_son_agence(
    client_agent: TestClient, societaire_autre_agence: str
) -> None:
    reponse = client_agent.post("/api/v1/scoring/confirm", json=_demande(societaire_autre_agence))
    assert reponse.status_code == 403


def test_superviseur_ne_peut_pas_previsualiser(
    client_superviseur: TestClient, societaire_agence_agent: str
) -> None:
    # Le superviseur parametre la grille (POST /parametrage/grille) mais ne doit pas pouvoir
    # aussi octroyer un credit lui-meme — separation des devoirs.
    reponse = client_superviseur.post(
        "/api/v1/scoring/preview", json=_demande(societaire_agence_agent)
    )
    assert reponse.status_code == 403


def test_superviseur_ne_peut_pas_confirmer(
    client_superviseur: TestClient, societaire_agence_agent: str
) -> None:
    reponse = client_superviseur.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_agence_agent)
    )
    assert reponse.status_code == 403


def test_decision_id_non_uuid_renvoie_422(client_agent: TestClient) -> None:
    reponse = client_agent.get("/api/v1/scoring/pas-un-uuid")
    assert reponse.status_code == 422
    assert reponse.json()["detail"]["code"] == "identifiant_invalide"


def test_decision_id_uuid_inexistant_renvoie_404(client_agent: TestClient) -> None:
    reponse = client_agent.get("/api/v1/scoring/00000000-0000-0000-0000-000000000000")
    assert reponse.status_code == 404


def test_sur_endettement_bloque_la_previsualisation(
    client_agent: TestClient, societaire_avec_credit_en_cours: str
) -> None:
    reponse = client_agent.post(
        "/api/v1/scoring/preview", json=_demande(societaire_avec_credit_en_cours)
    )
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "sur_endettement"


def test_sur_endettement_bloque_la_confirmation(
    client_agent: TestClient, societaire_avec_credit_en_cours: str
) -> None:
    reponse = client_agent.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_avec_credit_en_cours)
    )
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "sur_endettement"


def test_duree_demandee_excessive_est_rejetee(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    # Round 3 du pentest : une duree demesuree remontait en 500 (overflow) avant meme
    # d'atteindre la validation metier du catalogue produit.
    demande = _demande(societaire_agence_agent)
    demande["duree_demandee_mois"] = 99_999_999_999
    reponse = client_agent.post("/api/v1/scoring/preview", json=demande)
    assert reponse.status_code == 422


def test_deuxieme_octroi_pour_le_meme_societaire_est_bloque(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    # Round 3 du pentest (multi-octroi) : deux "accord" confirmes coup sur coup pour le meme
    # societaire passaient tous les deux, la table CORE-SIM n'ayant pas encore le temps de
    # refleter le premier credit. Deux demandes differentes (objet distinct) pour eviter la
    # deduplication de doublon exact deja en place.
    demande = _demande(societaire_agence_agent)
    demande["objet_credit"] = "equipement"
    premiere = client_agent.post("/api/v1/scoring/confirm", json=demande)
    assert premiere.status_code == 201
    if premiere.json()["tranche"] not in {"accord", "accord_sous_condition"}:
        pytest.skip("Le scoring de ce societaire ne produit pas un accord dans ce jeu de donnees")

    demande["objet_credit"] = "habitat"
    deuxieme = client_agent.post("/api/v1/scoring/confirm", json=demande)
    assert deuxieme.status_code == 422
    assert deuxieme.json()["code"] == "sur_endettement"


pytestmark_archivage = pytest.mark.skipif(
    "SEAWEEDFS_ACCESS_KEY" not in os.environ,
    reason="SeaweedFS absent : archivage non testable ici",
)


@pytestmark_archivage
def test_telecharger_la_fiche_en_pdf(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_agence_agent)
    )
    decision_id = reponse_scoring.json()["decision_id"]

    reponse_pdf = client_agent.get(f"/api/v1/scoring/{decision_id}/fiche/pdf")
    assert reponse_pdf.status_code == 200
    assert reponse_pdf.headers["content-type"] == "application/pdf"
    assert reponse_pdf.content[:4] == b"%PDF"


@pytestmark_archivage
def test_archiver_une_fiche(client_agent: TestClient, societaire_agence_agent: str) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirm", json=_demande(societaire_agence_agent)
    )
    decision_id = reponse_scoring.json()["decision_id"]

    reponse_archivage = client_agent.post(f"/api/v1/scoring/{decision_id}/archive")
    assert reponse_archivage.status_code == 200
    assert reponse_archivage.json()["fiche_id"]

    moteur = create_engine(os.environ["SOLIDA_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT chemin_objet FROM fiche_archivee WHERE decision_id = :id"),
            {"id": decision_id},
        ).first()
    assert ligne is not None
    assert ligne.chemin_objet.startswith("fiches/")
