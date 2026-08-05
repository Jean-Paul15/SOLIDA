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
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"},
    )
    return client


@pytest.fixture
def client_auditeur() -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "auditeur.interne", "mot_de_passe": "solida-demo"},
    )
    return client


@pytest.fixture(scope="module")
def societaire_agence_agent() -> str:
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("SELECT societaire_id FROM societaires WHERE caisse_id = 'CAI-00' LIMIT 1")
        ).first()
    assert ligne is not None
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
        "produit_id": "prod-commerce",
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

    reponse = client_agent.post(
        "/api/v1/scoring/previsualiser", json=_demande(societaire_agence_agent)
    )
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["montant_demande"] == 100000
    assert resultat["tranche"] in {"accord", "accord_sous_condition", "comite_de_credit", "refus"}
    # ModeleConstant ne produit aucune contribution par variable (probabilité fixe, les
    # features ne l'influencent pas) : la décomposition réelle n'existera qu'avec le vrai
    # modèle. Le mapper est déjà câblé pour l'afficher dès qu'elle existera (voir
    # docs/backend/03-decisions-provisoires-a-revoir.md).
    assert resultat["decomposition"] == []

    with moteur.connect() as connexion:
        apres = connexion.execute(text("SELECT count(*) FROM decision_scoring")).scalar_one()
    assert apres == avant


def test_confirmer_puis_relire_la_decision(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirmer", json=_demande(societaire_agence_agent)
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


def test_confirmer_un_societaire_introuvable_renvoie_404(client_agent: TestClient) -> None:
    reponse = client_agent.post("/api/v1/scoring/confirmer", json=_demande("SOC-INEXISTANT"))
    assert reponse.status_code == 404


def test_auditeur_ne_peut_pas_scorer(
    client_auditeur: TestClient, societaire_agence_agent: str
) -> None:
    reponse = client_auditeur.post(
        "/api/v1/scoring/confirmer", json=_demande(societaire_agence_agent)
    )
    assert reponse.status_code == 403


def test_agent_ne_peut_pas_scorer_hors_de_son_agence(
    client_agent: TestClient, societaire_autre_agence: str
) -> None:
    reponse = client_agent.post(
        "/api/v1/scoring/confirmer", json=_demande(societaire_autre_agence)
    )
    assert reponse.status_code == 403


pytestmark_archivage = pytest.mark.skipif(
    "SEAWEEDFS_ACCESS_KEY" not in os.environ,
    reason="SeaweedFS absent : archivage non testable ici",
)


@pytestmark_archivage
def test_telecharger_la_fiche_en_pdf(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirmer", json=_demande(societaire_agence_agent)
    )
    decision_id = reponse_scoring.json()["decision_id"]

    reponse_pdf = client_agent.get(f"/api/v1/scoring/{decision_id}/fiche/pdf")
    assert reponse_pdf.status_code == 200
    assert reponse_pdf.headers["content-type"] == "application/pdf"
    assert reponse_pdf.content[:4] == b"%PDF"


@pytestmark_archivage
def test_archiver_une_fiche(client_agent: TestClient, societaire_agence_agent: str) -> None:
    reponse_scoring = client_agent.post(
        "/api/v1/scoring/confirmer", json=_demande(societaire_agence_agent)
    )
    decision_id = reponse_scoring.json()["decision_id"]

    reponse_archivage = client_agent.post(f"/api/v1/scoring/{decision_id}/archiver")
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

