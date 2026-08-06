import asyncio
import os
import uuid

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


@pytest.fixture(scope="module", autouse=True)
def comptes_demo_provisionnes() -> None:
    """Rejoue le provisioning avant ce module : les tests supposent l'état documenté par le
    README (migrations puis `cli_provisionner_comptes demo`), pas seulement les migrations."""
    from solida.infrastructure.cli_provisionner_comptes import provisionner_demo

    provisionner_demo()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_connexion_avec_identifiants_valides_pose_le_cookie(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"},
    )

    # Compte de démo provisionné via `cli_provisionner_comptes demo`, exempté du changement
    # de mot de passe forcé (voir provisionner_demo) : False, pas True.
    assert reponse.status_code == 200
    assert reponse.json() == {
        "nom": "Agent Bè",
        "role": "agent",
        "agence": "CAI-00",
        "doit_changer_mot_de_passe": False,
    }
    assert "solida_session" in reponse.cookies


def test_connexion_avec_mauvais_mot_de_passe_refuse(client: TestClient) -> None:
    # Pas "agent.be" : cette identifiant est partagé par de nombreux autres tests qui s'y
    # connectent avec succès, un échec de trop l'exposerait au verrouillage après 5 échecs.
    from solida.infrastructure.cli_provisionner_comptes import creer_compte

    identifiant = f"compte.mdp.incorrect.test.{uuid.uuid4().hex[:8]}"
    creer_compte(
        identifiant=identifiant,
        nom_complet="Compte Test Mot De Passe Incorrect",
        role="agent",
        agence_id="CAI-00",
        mot_de_passe="solida-demo",
    )

    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": identifiant, "mot_de_passe": "mauvais"},
    )

    assert reponse.status_code == 401


def test_connexion_avec_identifiant_inconnu_refuse(client: TestClient) -> None:
    # Identifiant unique par exécution, même raison que test_connexion_se_verrouille_apres_...
    reponse = client.post(
        "/api/v1/auth/connexion",
        json={
            "identifiant": f"nexiste.pas.{uuid.uuid4().hex[:8]}",
            "mot_de_passe": "solida-demo",
        },
    )

    assert reponse.status_code == 401


def test_moi_relit_lutilisateur_depuis_le_cookie_de_connexion(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "agent.agoe", "mot_de_passe": "solida-demo"},
    )

    reponse = client.get("/api/v1/auth/moi")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "nom": "Agent Agoè",
        "role": "agent",
        "agence": "CAI-01",
        "doit_changer_mot_de_passe": False,
    }


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


def test_connexion_se_verrouille_apres_cinq_echecs(client: TestClient) -> None:
    # Identifiant unique par exécution : la fenêtre de verrouillage est de 15 minutes,
    # un identifiant fixe ferait interférer deux lancements rapprochés de la suite.
    identifiant = f"compte.verrouillage.test.{uuid.uuid4().hex[:8]}"
    for _ in range(5):
        reponse = client.post(
            "/api/v1/auth/connexion",
            json={"identifiant": identifiant, "mot_de_passe": "mauvais"},
        )
        assert reponse.status_code == 401

    reponse_bloquee = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": identifiant, "mot_de_passe": "mauvais"},
    )
    assert reponse_bloquee.status_code == 429


def test_une_nouvelle_connexion_revoque_la_precedente() -> None:
    premier_client = TestClient(app)
    premier_client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "administrateur.systeme", "mot_de_passe": "solida-demo"},
    )
    jeton_initial = premier_client.cookies.get("solida_session")
    assert jeton_initial is not None

    second_client = TestClient(app)
    second_client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "administrateur.systeme", "mot_de_passe": "solida-demo"},
    )

    premier_client.cookies.set("solida_session", jeton_initial)
    reponse = premier_client.get("/api/v1/auth/moi")
    assert reponse.status_code == 401


def test_changer_mot_de_passe_avec_mot_de_passe_actuel_incorrect_refuse(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "auditeur.interne", "mot_de_passe": "solida-demo"},
    )

    reponse = client.post(
        "/api/v1/auth/changer-mot-de-passe",
        json={"mot_de_passe_actuel": "mauvais", "nouveau_mot_de_passe": "un-nouveau-mdp-solide"},
    )

    assert reponse.status_code == 403


def test_changer_mot_de_passe_refuse_un_mot_de_passe_trop_court(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "auditeur.interne", "mot_de_passe": "solida-demo"},
    )

    reponse = client.post(
        "/api/v1/auth/changer-mot-de-passe",
        json={"mot_de_passe_actuel": "solida-demo", "nouveau_mot_de_passe": "court"},
    )

    assert reponse.status_code == 400


def test_changer_mot_de_passe_reussit_et_leve_le_drapeau(client: TestClient) -> None:
    # Compte jetable, identifiant unique par exécution : la réussite du changement modifie
    # durablement le mot de passe (creer_compte ne le réémet jamais sur un conflit), un
    # identifiant fixe casserait un second lancement de la suite avec l'ancien mot de passe.
    from solida.infrastructure.cli_provisionner_comptes import creer_compte

    identifiant = f"compte.changement.test.{uuid.uuid4().hex[:8]}"
    creer_compte(
        identifiant=identifiant,
        nom_complet="Compte Test Changement",
        role="agent",
        agence_id="CAI-00",
        mot_de_passe="solida-demo",
    )
    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": identifiant, "mot_de_passe": "solida-demo"},
    )

    reponse = client.post(
        "/api/v1/auth/changer-mot-de-passe",
        json={
            "mot_de_passe_actuel": "solida-demo",
            "nouveau_mot_de_passe": "un-nouveau-mdp-solide",
        },
    )
    assert reponse.status_code == 200

    reponse_connexion = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": identifiant, "mot_de_passe": "un-nouveau-mdp-solide"},
    )
    assert reponse_connexion.status_code == 200
    assert reponse_connexion.json()["doit_changer_mot_de_passe"] is False


def test_une_session_inactive_depuis_plus_de_15_minutes_expire(client: TestClient) -> None:
    import sqlalchemy as sa

    from solida.infrastructure.database import moteur_solida

    client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": "superviseur.reseau", "mot_de_passe": "solida-demo"},
    )
    jeton = client.cookies.get("solida_session")
    assert jeton is not None

    with moteur_solida().begin() as connexion:
        connexion.execute(
            sa.text("""
                UPDATE access_token SET derniere_activite_le = now() - interval '16 minutes'
                WHERE token = :jeton
            """),
            {"jeton": jeton},
        )

    reponse = client.get("/api/v1/auth/moi")
    assert reponse.status_code == 401


def test_un_compte_bloque_ne_peut_plus_se_connecter(client: TestClient) -> None:
    # Identifiant unique par exécution : chaque tentative sur un compte bloqué journalise
    # un échec, un identifiant fixe finirait par déclencher le verrouillage lui-même.
    from solida.infrastructure.cli_provisionner_comptes import bloquer_compte, creer_compte

    identifiant = f"compte.blocage.test.{uuid.uuid4().hex[:8]}"
    creer_compte(
        identifiant=identifiant,
        nom_complet="Compte Test Blocage",
        role="agent",
        agence_id="CAI-00",
        mot_de_passe="solida-demo",
    )
    bloquer_compte(identifiant)

    reponse = client.post(
        "/api/v1/auth/connexion",
        json={"identifiant": identifiant, "mot_de_passe": "solida-demo"},
    )
    assert reponse.status_code == 401
