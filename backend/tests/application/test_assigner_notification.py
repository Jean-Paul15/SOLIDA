from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from solida.application.use_cases.assigner_notification import AssignerNotification
from solida.domain.errors import AccesRefuse
from solida.domain.values.demande_societaire import STATUT_NOUVELLE, DemandeSocietaire
from solida.domain.values.utilisateur import UtilisateurResume


def _demande(agence_id: str, assigne_a_agent_id: str | None = None) -> DemandeSocietaire:
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


def _agent(agent_id: str, agence_id: str | None, desactive: bool = False) -> UtilisateurResume:
    return UtilisateurResume(
        id=agent_id,
        nom_complet="Agent Test",
        role="agent",
        agence_id=agence_id,
        desactive_le=datetime.now(UTC) if desactive else None,
    )


@dataclass
class _FakeDemandeSocietaireRepository:
    demande: DemandeSocietaire | None
    assignee: tuple[str, str] | None = None

    def lire(self, demande_id: str) -> DemandeSocietaire | None:
        return self.demande

    def assigner(self, demande_id: str, agent_id: str) -> DemandeSocietaire | None:
        self.assignee = (demande_id, agent_id)
        assert self.demande is not None
        return DemandeSocietaire(**{**self.demande.__dict__, "assigne_a_agent_id": agent_id})


@dataclass
class _FakeUtilisateurRepository:
    utilisateurs: dict[str, UtilisateurResume] = field(default_factory=dict)

    def lire(self, utilisateur_id: str) -> UtilisateurResume | None:
        return self.utilisateurs.get(utilisateur_id)

    def lister_agents_agence(self, agence_id: str) -> list[UtilisateurResume]:
        return [u for u in self.utilisateurs.values() if u.agence_id == agence_id]


def test_assignation_reussie_meme_agence() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-00"))
    utilisateurs = _FakeUtilisateurRepository({"AGENT-1": _agent("AGENT-1", "CAI-00")})
    use_case = AssignerNotification(demandes, utilisateurs)

    resultat = use_case.execute("D1", "CAI-00", "AGENT-1")

    assert resultat is not None
    assert demandes.assignee == ("D1", "AGENT-1")


def test_refus_si_agent_cible_dune_autre_agence() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-00"))
    utilisateurs = _FakeUtilisateurRepository({"AGENT-1": _agent("AGENT-1", "CAI-01")})
    use_case = AssignerNotification(demandes, utilisateurs)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "CAI-00", "AGENT-1")


def test_refus_si_cible_na_pas_le_role_agent() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-00"))
    superviseur = UtilisateurResume(
        id="SUP-1", nom_complet="Sup", role="superviseur", agence_id="CAI-00", desactive_le=None
    )
    utilisateurs = _FakeUtilisateurRepository({"SUP-1": superviseur})
    use_case = AssignerNotification(demandes, utilisateurs)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "CAI-00", "SUP-1")


def test_refus_si_agent_cible_desactive() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-00"))
    utilisateurs = _FakeUtilisateurRepository(
        {"AGENT-1": _agent("AGENT-1", "CAI-00", desactive=True)}
    )
    use_case = AssignerNotification(demandes, utilisateurs)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "CAI-00", "AGENT-1")


def test_refus_si_deja_assignee() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-00", assigne_a_agent_id="AGENT-0"))
    utilisateurs = _FakeUtilisateurRepository({"AGENT-1": _agent("AGENT-1", "CAI-00")})
    use_case = AssignerNotification(demandes, utilisateurs)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "CAI-00", "AGENT-1")


def test_refus_si_superviseur_dagence_hors_de_son_perimetre() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-01"))
    utilisateurs = _FakeUtilisateurRepository({"AGENT-1": _agent("AGENT-1", "CAI-01")})
    use_case = AssignerNotification(demandes, utilisateurs)

    with pytest.raises(AccesRefuse):
        use_case.execute("D1", "CAI-00", "AGENT-1")


def test_superviseur_reseau_peut_assigner_nimporte_quelle_agence() -> None:
    demandes = _FakeDemandeSocietaireRepository(_demande("CAI-01"))
    utilisateurs = _FakeUtilisateurRepository({"AGENT-1": _agent("AGENT-1", "CAI-01")})
    use_case = AssignerNotification(demandes, utilisateurs)

    resultat = use_case.execute("D1", None, "AGENT-1")

    assert resultat is not None


def test_demande_introuvable_renvoie_none() -> None:
    demandes = _FakeDemandeSocietaireRepository(None)
    utilisateurs = _FakeUtilisateurRepository({})
    use_case = AssignerNotification(demandes, utilisateurs)

    assert use_case.execute("D1", "CAI-00", "AGENT-1") is None
