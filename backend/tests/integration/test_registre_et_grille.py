import os
import uuid

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


def _payload_grille(version_grille: str, **surcharges_grille: float) -> dict[str, object]:
    grille = {
        "marge": 0.15,
        "lgd": 0.75,
        "multiplicateur_accord": 0.6,
        "multiplicateur_vigilance": 1.0,
        "multiplicateur_examen": 1.6,
        **surcharges_grille,
    }
    return {
        "version_grille": version_grille,
        "grille": grille,
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
    }


def test_registre_est_accessible_a_tout_role_authentifie() -> None:
    reponse = _connecte("auditeur.interne").get("/api/v1/registre")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert "elements" in corps
    assert "total" in corps


def test_registre_avec_limite_excessive_est_rejete() -> None:
    # Plafond serveur sur `limite`, independant de ce que le client demande.
    reponse = _connecte("auditeur.interne").get("/api/v1/registre", params={"limite": 999999})
    assert reponse.status_code == 422


def test_registre_avec_limite_ou_decalage_negatif_est_rejete() -> None:
    # Round 3 du pentest : une valeur negative atteignait le LIMIT/OFFSET SQL et remontait
    # en 500 brut au lieu d'un 422 propre.
    client = _connecte("auditeur.interne")
    assert client.get("/api/v1/registre", params={"limite": -1}).status_code == 422
    assert client.get("/api/v1/registre", params={"decalage": -1}).status_code == 422


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
        "/api/v1/parametrage/grille", json=_payload_grille("v0.2-refusee")
    )
    assert reponse.status_code == 403


def test_marge_hors_bornes_est_rejetee() -> None:
    # Les bornes du slider UI (5-30%) doivent aussi etre imposees cote serveur.
    reponse = _connecte("superviseur.reseau").post(
        "/api/v1/parametrage/grille", json=_payload_grille("v0.3-marge-hors-bornes", marge=5.0)
    )
    assert reponse.status_code == 422


def test_version_grille_trop_longue_est_rejetee() -> None:
    reponse = _connecte("superviseur.reseau").post(
        "/api/v1/parametrage/grille", json=_payload_grille("v" * 40)
    )
    assert reponse.status_code == 422


def test_scorecard_modifie_est_rejete() -> None:
    # pdo/score_reference/odds_reference ne sont plus editables par ce canal (round 3 du
    # pentest : un appel API direct pouvait changer la mise a l'echelle du score pour tout le
    # reseau sans aucun garde-fou, alors que l'ecran ne le permet plus).
    payload = _payload_grille("v0.5-scorecard-modifie")
    payload["scorecard"] = {"pdo": 5.0, "score_reference": 600, "odds_reference": 50}
    reponse = _connecte("superviseur.reseau").post("/api/v1/parametrage/grille", json=payload)
    assert reponse.status_code == 422
    assert reponse.json()["code"] == "scorecard_immuable"


def test_doublon_version_grille_renvoie_409_puis_une_version_unique_reussit() -> None:
    # Un doublon doit renvoyer 409 (pas 500), et surtout ne doit pas casser durablement
    # l'endpoint pour les ecritures suivantes valides dans le meme process. Suffixe unique :
    # la base de test n'est pas reinitialisee entre deux executions manuelles de la suite,
    # un nom de version fixe entrerait en collision avec un run precedent.
    client = _connecte("superviseur.reseau")
    # Reste sous max_length=30 (schemas/grille.py) meme avec le suffixe "-suite" ci-dessous.
    version = f"v-doublon-{uuid.uuid4().hex[:8]}"

    premiere = client.post("/api/v1/parametrage/grille", json=_payload_grille(version))
    assert premiere.status_code == 200

    doublon = client.post("/api/v1/parametrage/grille", json=_payload_grille(version))
    assert doublon.status_code == 409
    assert doublon.json()["code"] == "version_deja_existante"

    ensuite = client.post("/api/v1/parametrage/grille", json=_payload_grille(f"{version}-suite"))
    assert ensuite.status_code == 200
