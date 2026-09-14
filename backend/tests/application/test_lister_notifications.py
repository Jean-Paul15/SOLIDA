from dataclasses import dataclass, field
from datetime import UTC, date, datetime

from solida.application.use_cases.lister_notifications import ListerNotifications
from solida.domain.entities.societaire import Societaire
from solida.domain.values.demande_societaire import STATUT_NOUVELLE, DemandeSocietaire


def _demande(demande_id: str, agence_id: str, assigne_a_agent_id: str | None) -> DemandeSocietaire:
    return DemandeSocietaire(
        demande_id=demande_id,
        societaire_id=f"SOC-{demande_id}",
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


def _societaire(societaire_id: str) -> Societaire:
    return Societaire(
        societaire_id=societaire_id,
        numero_membre="100000",
        nom_complet="Test Societaire",
        agence="CAI-00",
        date_adhesion=date(2020, 1, 1),
        anciennete_mois=48,
        segment="individuel",
        age=35,
        zone="urbain",
        nb_personnes_a_charge=2,
        niveau_instruction=None,
        parts_sociales_montant=10000,
        revenu_mensuel_declare=100000,
        groupe_id=None,
        a_credit_en_cours=False,
    )


@dataclass
class _FakeDemandeSocietaireRepository:
    demandes: list[DemandeSocietaire] = field(default_factory=list)

    def lister_non_assignees(
        self, agence_id: str | None, statut: str, limite: int, decalage: int
    ) -> list[DemandeSocietaire]:
        return [
            d
            for d in self.demandes
            if (agence_id is None or d.agence_id == agence_id)
            and d.statut == statut
            and d.assigne_a_agent_id is None
        ]

    def compter_non_assignees(self, agence_id: str | None, statut: str) -> int:
        return len(self.lister_non_assignees(agence_id, statut, 999, 0))

    def lister_assignees(
        self, agence_id: str | None, agent_id: str, statut: str, limite: int, decalage: int
    ) -> list[DemandeSocietaire]:
        return [
            d
            for d in self.demandes
            if (agence_id is None or d.agence_id == agence_id)
            and d.statut == statut
            and d.assigne_a_agent_id == agent_id
        ]

    def compter_assignees(self, agence_id: str | None, agent_id: str, statut: str) -> int:
        return len(self.lister_assignees(agence_id, agent_id, statut, 999, 0))


@dataclass
class _FakeCoreSimReader:
    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return _societaire(societaire_id)


def test_agent_ne_voit_que_ses_demandes_assignees() -> None:
    demandes = [
        _demande("D1", "CAI-00", assigne_a_agent_id="AGENT-1"),
        _demande("D2", "CAI-00", assigne_a_agent_id="AGENT-2"),
        _demande("D3", "CAI-00", assigne_a_agent_id=None),
    ]
    use_case = ListerNotifications(
        demande_societaire_repository=_FakeDemandeSocietaireRepository(demandes),
        core_sim_reader=_FakeCoreSimReader(),
    )

    affichees, total = use_case.execute("agent", "AGENT-1", "CAI-00", limite=20, decalage=0)

    assert [a.demande.demande_id for a in affichees] == ["D1"]
    assert total == 1


def test_superviseur_dagence_ne_voit_que_les_non_assignees_de_son_agence() -> None:
    demandes = [
        _demande("D1", "CAI-00", assigne_a_agent_id=None),
        _demande("D2", "CAI-00", assigne_a_agent_id="AGENT-1"),
        _demande("D3", "CAI-01", assigne_a_agent_id=None),
    ]
    use_case = ListerNotifications(
        demande_societaire_repository=_FakeDemandeSocietaireRepository(demandes),
        core_sim_reader=_FakeCoreSimReader(),
    )

    affichees, total = use_case.execute("superviseur", "SUP-1", "CAI-00", limite=20, decalage=0)

    assert [a.demande.demande_id for a in affichees] == ["D1"]
    assert total == 1


def test_superviseur_reseau_voit_les_non_assignees_de_toutes_les_agences() -> None:
    demandes = [
        _demande("D1", "CAI-00", assigne_a_agent_id=None),
        _demande("D2", "CAI-01", assigne_a_agent_id=None),
        _demande("D3", "CAI-01", assigne_a_agent_id="AGENT-1"),
    ]
    use_case = ListerNotifications(
        demande_societaire_repository=_FakeDemandeSocietaireRepository(demandes),
        core_sim_reader=_FakeCoreSimReader(),
    )

    affichees, total = use_case.execute("superviseur", "SUP-1", None, limite=20, decalage=0)

    assert {a.demande.demande_id for a in affichees} == {"D1", "D2"}
    assert total == 2
