import os

import pytest
from fastapi.testclient import TestClient

from solida.infrastructure.application_fastapi import app

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ or "CORESIM_DATABASE_URL" not in os.environ,
    reason="Bases reelles absentes : integration non disponible ici",
)


def _connecte(identifiant: str) -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/connexion", json={"identifiant": identifiant, "mot_de_passe": "solida-demo"}
    )
    return client


def test_registre_est_accessible_a_tout_role_authentifie() -> None:
    reponse = _connecte("auditeur.interne").get("/api/v1/registre")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert "elements" in corps
    assert "total" in corps


def test_lecture_grille_autorisee_a_lagent() -> None:
    # L'agent doit pouvoir situer un score par rapport aux seuils de la grille qui a produit
    # sa décision (explicabilité) ; seule la modification (POST) reste réservée à la supervision.
    reponse = _connecte("agent.be").get("/api/v1/parametrage/grille")
    assert reponse.status_code == 200


def test_modification_grille_refusee_a_lagent() -> None:
    reponse = _connecte("agent.be").post(
        "/api/v1/parametrage/grille",
        json={
            "version_grille": "v0.2-refusee",
            "grille": {
                "marge": 0.15,
                "lgd": 0.75,
                "multiplicateur_accord": 0.6,
                "multiplicateur_vigilance": 1.0,
                "multiplicateur_examen": 1.6,
            },
            "progressif": {
                "coefficient_progression": 1.5,
                "montant_plancher": 50000,
                "plafonds_produits": {"prod-individuel": 2000000},
                "plafond_primo_emprunteur": 150000,
                "modulation_base": 1.3,
                "modulation_pente": 2.0,
                "modulation_min": 0.4,
                "modulation_max": 1.2,
            },
            "scorecard": {"pdo": 20, "score_reference": 600, "odds_reference": 50},
        },
    )
    assert reponse.status_code == 403


def test_lecture_grille_autorisee_au_superviseur() -> None:
    reponse = _connecte("superviseur.reseau").get("/api/v1/parametrage/grille")
    assert reponse.status_code == 200
    assert reponse.json()["active"] is True


def test_modification_grille_refusee_a_lauditeur() -> None:
    reponse = _connecte("auditeur.interne").post(
        "/api/v1/parametrage/grille",
        json={
            "version_grille": "v0.2-refusee",
            "grille": {
                "marge": 0.15,
                "lgd": 0.75,
                "multiplicateur_accord": 0.6,
                "multiplicateur_vigilance": 1.0,
                "multiplicateur_examen": 1.6,
            },
            "progressif": {
                "coefficient_progression": 1.5,
                "montant_plancher": 50000,
                "plafonds_produits": {"prod-individuel": 2000000},
                "plafond_primo_emprunteur": 150000,
                "modulation_base": 1.3,
                "modulation_pente": 2.0,
                "modulation_min": 0.4,
                "modulation_max": 1.2,
            },
            "scorecard": {"pdo": 20, "score_reference": 600, "odds_reference": 50},
        },
    )
    assert reponse.status_code == 403
