"""J2 (clôture) : le routage des notifications passe désormais par le superviseur d'agence,
qui assigne à un agent précis — plus de boîte partagée où tous les agents d'une agence voient
tout. Ce test rejoue le scénario complet contre l'application réelle (TestClient + Postgres
SOLIDA réel), pas seulement les cas d'usage unitaires (déjà couverts avec des doublures dans
`backend/tests/application/test_{lister,assigner,archiver}_notification.py`)."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from solida.adapters.persistence.demande_societaire_repository_sql import (
    SqlDemandeSocietaireRepository,
)
from solida.domain.values.decision import DecisionAEnregistrer
from solida.domain.values.demande_societaire import DemandeSocietaireACreer
from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.montant import Montant
from solida.domain.values.score import Score
from solida.domain.values.tranche import TrancheDecision
from solida.infrastructure.application_fastapi import app

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ or "CORESIM_DATABASE_URL" not in os.environ,
    reason="Bases reelles absentes : integration non disponible ici",
)

AGENCE = "CAI-00"


def _connecter(client: TestClient, identifiant: str) -> None:
    reponse = client.post(
        "/api/v1/auth/login", json={"identifiant": identifiant, "mot_de_passe": "solida-demo"}
    )
    assert reponse.status_code == 200, reponse.text


def _creer_demande_nouvelle() -> str:
    demande_id = str(uuid.uuid4())
    resultat = DecisionAEnregistrer(
        decision_id=str(uuid.uuid4()),
        agent_id="n/a",
        agent_nom="n/a",
        agent_agence_id=None,
        societaire_id="SOC-TEST-NOTIF",
        entree={},
        features_utilisees={},
        probabilite=0.1,
        score=Score(valeur=600),
        tranche=TrancheDecision.ACCORD,
        montant_recommande=Montant(valeur=100_000),
        mode_calcul=ModeCalcul.SOCLE_SEUL,
        motif_mode=None,
        points_de_base=600,
        decomposition=[],
        plafond_progressif=Montant(valeur=100_000),
        trajectoire_progression=[],
        conditions_reexamen=[],
        avertissements=[],
        version_modele="v-test",
        version_grille="v-test",
    )
    repository = SqlDemandeSocietaireRepository(create_engine(os.environ["SOLIDA_DATABASE_URL"]))
    demande = repository.enregistrer(
        DemandeSocietaireACreer(
            demande_id=demande_id,
            societaire_id="SOC-TEST-NOTIF",
            agence_id=AGENCE,
            montant_demande=100_000,
            objet_credit="stock",
            duree_mois=6,
            produit_id="prod-individuel",
            resultat=resultat,
        )
    )
    return demande.demande_id


def _ids_notifications(reponse_json: dict) -> set[str]:
    return {e["demande_id"] for e in reponse_json["elements"]}


def test_flux_complet_superviseur_assigne_puis_agent_traite() -> None:
    demande_id = _creer_demande_nouvelle()

    client_agent = TestClient(app)
    _connecter(client_agent, "agent.be")
    reponse_avant = client_agent.get("/api/v1/notifications?limite=50")
    assert reponse_avant.status_code == 200
    assert demande_id not in _ids_notifications(reponse_avant.json())

    client_superviseur = TestClient(app)
    _connecter(client_superviseur, "superviseur.cai00")
    reponse_superviseur_avant = client_superviseur.get("/api/v1/notifications?limite=50")
    assert reponse_superviseur_avant.status_code == 200
    assert demande_id in _ids_notifications(reponse_superviseur_avant.json())

    reponse_agents = client_superviseur.get("/api/v1/notifications/agents")
    assert reponse_agents.status_code == 200
    agents = reponse_agents.json()
    agent_be = next(a for a in agents if a["nom_complet"] == "Agent Bè")

    reponse_assignation = client_superviseur.post(
        f"/api/v1/notifications/{demande_id}/assigner", json={"agent_id": agent_be["id"]}
    )
    assert reponse_assignation.status_code == 200, reponse_assignation.text
    assert reponse_assignation.json()["assigne_a_agent_id"] == agent_be["id"]

    reponse_superviseur_apres = client_superviseur.get("/api/v1/notifications?limite=50")
    assert demande_id not in _ids_notifications(reponse_superviseur_apres.json())

    reponse_agent_apres = client_agent.get("/api/v1/notifications?limite=50")
    assert demande_id in _ids_notifications(reponse_agent_apres.json())

    client_agent_agoe = TestClient(app)
    _connecter(client_agent_agoe, "agent.agoe")
    reponse_archivage_refuse = client_agent_agoe.post(
        f"/api/v1/notifications/{demande_id}/archiver"
    )
    assert reponse_archivage_refuse.status_code == 403

    reponse_archivage = client_agent.post(f"/api/v1/notifications/{demande_id}/archiver")
    assert reponse_archivage.status_code == 200
    assert reponse_archivage.json()["statut"] == "archivee"


def test_agent_ne_peut_pas_assigner() -> None:
    demande_id = _creer_demande_nouvelle()
    client_agent = TestClient(app)
    _connecter(client_agent, "agent.be")

    reponse = client_agent.post(
        f"/api/v1/notifications/{demande_id}/assigner", json={"agent_id": "peu-importe"}
    )
    assert reponse.status_code == 403


def test_lister_agents_ne_renvoie_que_ceux_de_lagence_du_superviseur() -> None:
    client_superviseur = TestClient(app)
    _connecter(client_superviseur, "superviseur.cai00")

    reponse = client_superviseur.get("/api/v1/notifications/agents")
    assert reponse.status_code == 200
    noms = {a["nom_complet"] for a in reponse.json()}
    assert "Agent Bè" in noms
    assert "Agent Agoè" not in noms


def test_superviseur_dagence_ignore_le_parametre_agence_id() -> None:
    """Un superviseur d'agence ne doit jamais pouvoir consulter une autre agence en
    manipulant le paramètre de requête : sa propre agence prime toujours."""
    client_superviseur = TestClient(app)
    _connecter(client_superviseur, "superviseur.cai00")

    reponse = client_superviseur.get("/api/v1/notifications/agents?agence_id=CAI-01")
    assert reponse.status_code == 200
    noms = {a["nom_complet"] for a in reponse.json()}
    assert "Agent Bè" in noms
    assert "Agent Agoè" not in noms


def test_superviseur_reseau_doit_preciser_une_agence() -> None:
    client_superviseur = TestClient(app)
    _connecter(client_superviseur, "superviseur.reseau")

    reponse = client_superviseur.get("/api/v1/notifications/agents")
    assert reponse.status_code == 400
    assert reponse.json()["detail"]["code"] == "agence_requise"


def test_superviseur_reseau_peut_lister_les_agents_dune_agence_precisee() -> None:
    client_superviseur = TestClient(app)
    _connecter(client_superviseur, "superviseur.reseau")

    reponse = client_superviseur.get("/api/v1/notifications/agents?agence_id=CAI-01")
    assert reponse.status_code == 200
    noms = {a["nom_complet"] for a in reponse.json()}
    assert "Agent Agoè" in noms
    assert "Agent Bè" not in noms
