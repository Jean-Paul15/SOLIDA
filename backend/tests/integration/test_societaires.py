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


def test_recherche_sous_deux_caracteres_renvoie_une_liste_vide(client_agent: TestClient) -> None:
    reponse = client_agent.get("/api/v1/societaires/search", params={"terme": "A"})
    assert reponse.status_code == 200
    assert reponse.json() == {"elements": [], "total": 0}


def test_recherche_ne_renvoie_que_lagence_de_lagent(client_agent: TestClient) -> None:
    reponse = client_agent.get("/api/v1/societaires/search", params={"terme": "an", "limite": 50})
    assert reponse.status_code == 200
    elements = reponse.json()["elements"]
    assert elements
    assert all(e["agence"] == "CAI-00" for e in elements)


def test_recherche_avec_limite_excessive_est_rejetee(client_agent: TestClient) -> None:
    # Plafond serveur sur `limite`, independant de ce que le client demande.
    reponse = client_agent.get(
        "/api/v1/societaires/search", params={"terme": "an", "limite": 999999}
    )
    assert reponse.status_code == 422


def test_recherche_avec_limite_negative_est_rejetee(client_agent: TestClient) -> None:
    # Round 3 du pentest : une valeur negative atteignait le LIMIT SQL et remontait en 500
    # brut au lieu d'un 422 propre.
    reponse = client_agent.get("/api/v1/societaires/search", params={"terme": "an", "limite": -1})
    assert reponse.status_code == 422


def test_dossier_dun_societaire_de_son_agence_est_accessible(
    client_agent: TestClient, societaire_agence_agent: str
) -> None:
    reponse = client_agent.get(f"/api/v1/societaires/{societaire_agence_agent}/dossier")
    assert reponse.status_code == 200
    assert reponse.json()["identite"]["societaire_id"] == societaire_agence_agent


def test_dossier_dun_societaire_dune_autre_agence_est_refuse(
    client_agent: TestClient, societaire_autre_agence: str
) -> None:
    reponse = client_agent.get(f"/api/v1/societaires/{societaire_autre_agence}/dossier")
    assert reponse.status_code == 403


def test_dossier_introuvable_renvoie_404(client_agent: TestClient) -> None:
    reponse = client_agent.get("/api/v1/societaires/SOC-INEXISTANT/dossier")
    assert reponse.status_code == 404


def test_identifiant_de_forme_invalide_renvoie_422(client_agent: TestClient) -> None:
    # Round 3 du pentest : un `/` encode dans l'identifiant remontait en 500 brut. Selon que
    # le routeur decode `%2F` avant ou apres le matching de route, la reponse est soit 404
    # (route non trouvee) soit 422 (notre validation de forme) — les deux sont sans fuite,
    # jamais un 500 brut.
    reponse = client_agent.get("/api/v1/societaires/SOC-1%2F2/dossier")
    assert reponse.status_code in {404, 422}
    if reponse.status_code == 422:
        assert reponse.json()["detail"]["code"] == "identifiant_invalide"


def test_total_de_recherche_reflete_le_vrai_nombre_de_correspondances_pas_la_page(
    client_agent: TestClient,
) -> None:
    # Round 3 du pentest : `total` valait `len(elements)` (la taille de la page), pas le vrai
    # nombre de correspondances — indetectable qu'une recherche a beaucoup plus de resultats
    # que la page renvoyee. Une page plus petite doit avoir moins d'`elements` mais le meme
    # `total` qu'une page plus large, sur le meme terme.
    petite_page = client_agent.get(
        "/api/v1/societaires/search", params={"terme": "an", "limite": 1}
    ).json()
    grande_page = client_agent.get(
        "/api/v1/societaires/search", params={"terme": "an", "limite": 50}
    ).json()
    assert len(petite_page["elements"]) == 1
    assert petite_page["total"] == grande_page["total"]
    assert petite_page["total"] >= len(grande_page["elements"])
