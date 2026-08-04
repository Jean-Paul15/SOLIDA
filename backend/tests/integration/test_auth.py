import asyncio
import os

import pytest
from fastapi.testclient import TestClient

from solida.domain.erreurs import AccesRefuse
from solida.infrastructure.application_fastapi import app
from solida.infrastructure.auth import exige_role


class _UtilisateurFactice:
    def __init__(self, role: str) -> None:
        self.role = role


def test_exige_role_refuse_un_role_absent_de_la_liste() -> None:
    dependance = exige_role("superviseur", "administrateur")

    with pytest.raises(AccesRefuse):
        asyncio.run(dependance(_UtilisateurFactice("agent")))  # type: ignore[arg-type]


def test_exige_role_laisse_passer_un_role_autorise() -> None:
    dependance = exige_role("superviseur", "administrateur")
    utilisateur = _UtilisateurFactice("superviseur")

    resultat = asyncio.run(dependance(utilisateur))  # type: ignore[arg-type]

    assert resultat is utilisateur


pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ,
    reason="SOLIDA_DATABASE_URL_ASYNC absent : integration reelle non disponible ici",
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_connexion_avec_identifiants_valides_pose_le_cookie(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"nom": "Agent Bè", "agence": "CAI-00"}
    assert "solida_session" in reponse.cookies


def test_connexion_avec_mauvais_mot_de_passe_refuse(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.be", "mot_de_passe": "mauvais"},
    )

    assert reponse.status_code == 401


def test_connexion_avec_identifiant_inconnu_refuse(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "nexiste.pas", "mot_de_passe": "solida-demo"},
    )

    assert reponse.status_code == 401


def test_moi_relit_lutilisateur_depuis_le_cookie_de_connexion(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.agoe", "mot_de_passe": "solida-demo"},
    )

    reponse = client.get("/api/v1/auth/moi")

    assert reponse.status_code == 200
    assert reponse.json() == {"nom": "Agent Agoè", "agence": "CAI-01"}


def test_deconnexion_revoque_le_jeton_pas_seulement_le_cookie(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"},
    )
    jeton = client.cookies.get("solida_session")
    assert jeton is not None

    reponse_deconnexion = client.post("/api/v1/auth/deconnexion")
    assert reponse_deconnexion.status_code == 200

    client.cookies.set("solida_session", jeton)
    reponse_moi = client.get("/api/v1/auth/moi")
    assert reponse_moi.status_code == 401
