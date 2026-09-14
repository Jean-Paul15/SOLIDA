from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from solida.application.use_cases.archiver_notification import ArchiverNotification
from solida.domain.errors import AccesRefuse
from solida.domain.values.demande_societaire import STATUT_NOUVELLE, DemandeSocietaire


def _demande(agence_id: str, assigne_a_agent_id: str | None) -> DemandeSocietaire:
    return DemandeSocietaire(
        demande_id="D1",
        societaire_id="SOC-1",
        agence_id=agence_id,
        montant_demande=100_000,
        objet_credit="stock",
        duree_mois=6,
        produit_id="prod-individuel",
        resultat={},
        statut=STATUT_NOUVELLE,
        cree_le=datetime.now(UTC),
        assigne_a_agent_id=assigne_a_agent_id,
        archivee_le=None,
        archivee_par_agent_id=None,
    )


@dataclass
class _FakeDemandeSocietaireRepository:
    demande: DemandeSocietaire | None
    archivee_par: str | None = None

    def lire(self, demande_id: str) -> DemandeSocietaire | None:
        return self.demande

    def archiver(self, demande_id: str, agent_id: str) -> DemandeSocietaire | None:
        self.archivee_par = agent_id
        return self.demande


def test_refus_si_lagent_nest_pas_lassigne() -> None:
    repository = _FakeDemandeSocietaireRepository(_demande("CAI-00", "AGENT-1"))
    use_case = ArchiverNotification(repository)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "AGENT-2", "CAI-00")

    assert repository.archivee_par is None


def test_succes_si_lagent_est_lassigne() -> None:
    repository = _FakeDemandeSocietaireRepository(_demande("CAI-00", "AGENT-1"))
    use_case = ArchiverNotification(repository)

    resultat = use_case.execute("D1", "AGENT-1", "CAI-00")

    assert resultat is not None
    assert repository.archivee_par == "AGENT-1"


def test_refus_si_agence_differente() -> None:
    repository = _FakeDemandeSocietaireRepository(_demande("CAI-01", "AGENT-1"))
    use_case = ArchiverNotification(repository)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "AGENT-1", "CAI-00")


def test_demande_introuvable_renvoie_none() -> None:
    repository = _FakeDemandeSocietaireRepository(None)
    use_case = ArchiverNotification(repository)

    assert use_case.execute("D1", "AGENT-1", "CAI-00") is None
