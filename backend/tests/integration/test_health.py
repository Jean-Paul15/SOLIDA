from fastapi.testclient import TestClient

from solida.infrastructure.application_fastapi import app


def test_le_point_de_sante_repond_ok() -> None:
    client = TestClient(app)

    reponse = client.get("/api/v1/health")

    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}
