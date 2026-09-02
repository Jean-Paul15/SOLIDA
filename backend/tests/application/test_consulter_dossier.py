from dataclasses import dataclass
from datetime import date

from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.credit import Credit
from solida.domain.entities.groupe import GroupeCaution, MembreGroupe
from solida.domain.entities.mouvement_epargne import MouvementEpargne
from solida.domain.entities.societaire import Societaire


def _societaire(**overrides: object) -> Societaire:
    valeurs: dict[str, object] = {
        "societaire_id": "SOC-1",
        "numero_membre": "100001",
        "nom_complet": "Test Societaire",
        "agence": "CAI-00",
        "date_adhesion": date(2020, 1, 1),
        "anciennete_mois": 48,
        "segment": "individuel",
        "age": 35,
        "zone": "urbain",
        "nb_personnes_a_charge": 2,
        "niveau_instruction": None,
        "parts_sociales_montant": 10000,
        "revenu_mensuel_declare": 100000,
        "groupe_id": None,
        "a_credit_en_cours": False,
    }
    valeurs.update(overrides)
    return Societaire(**valeurs)  # type: ignore[arg-type]


def _credit(**overrides: object) -> Credit:
    valeurs: dict[str, object] = {
        "credit_id": "CR-1",
        "societaire_id": "SOC-1",
        "produit_id": "PROD-1",
        "date_deblocage": date(2023, 1, 1),
        "date_echeance_prevue": date(2024, 1, 1),
        "duree_mois": 12,
        "numero_cycle": 1,
        "montant_octroye": 200000,
        "statut": "en_cours",
        "jours_retard_max": None,
        "capital_restant_du": 100000,
    }
    valeurs.update(overrides)
    return Credit(**valeurs)  # type: ignore[arg-type]


def _membre(**overrides: object) -> MembreGroupe:
    valeurs: dict[str, object] = {
        "societaire_id": "SOC-2",
        "nom_complet": "Membre Groupe",
        "role": "membre",
        "anciennete_mois": 24,
        "statut_credit": "en_cours",
        "caution_appelee": False,
    }
    valeurs.update(overrides)
    return MembreGroupe(**valeurs)  # type: ignore[arg-type]


def _groupe(**overrides: object) -> GroupeCaution:
    valeurs: dict[str, object] = {
        "groupe_id": "GRP-1",
        "nom_groupe": "Groupe Test",
        "taille_actuelle": 5,
        "date_creation": date(2019, 1, 1),
        "taux_remboursement_groupe": 0.95,
        "nb_cycles_completes": 3,
        "nb_credits_anterieurs_soldes": 10,
        "nb_sorties_12m": 0,
        "statut": "actif",
        "membres": [_membre()],
    }
    valeurs.update(overrides)
    return GroupeCaution(**valeurs)  # type: ignore[arg-type]


@dataclass
class _FakeCoreSimReader:
    societaire: Societaire | None
    credits: list[Credit]
    compte: CompteEpargne | None
    groupe: GroupeCaution | None
    mouvements: list[MouvementEpargne]

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return self.societaire

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        return self.credits

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None:
        return self.compte

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None:
        return self.groupe

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]:
        return self.mouvements


def test_executer_renvoie_none_si_societaire_introuvable() -> None:
    use_case = ConsulterDossier(
        core_sim_reader=_FakeCoreSimReader(
            societaire=None, credits=[], compte=None, groupe=None, mouvements=[]
        )
    )

    assert use_case.execute("SOC-1") is None


def test_executer_compose_le_dossier_complet() -> None:
    use_case = ConsulterDossier(
        core_sim_reader=_FakeCoreSimReader(
            societaire=_societaire(),
            credits=[_credit()],
            compte=CompteEpargne(
                compte_id="CPT-1",
                societaire_id="SOC-1",
                solde_moyen_6m=50000,
                nb_mois_avec_depot_12m=10,
                croissance_12m=0.15,
                volatilite=0.2,
            ),
            groupe=_groupe(),
            mouvements=[
                MouvementEpargne(
                    mouvement_id="MVT-1",
                    compte_id="CPT-1",
                    date_operation=date(2024, 1, 1),
                    sens="depot",
                    montant=10000,
                )
            ],
        )
    )

    dossier = use_case.execute("SOC-1")

    assert dossier is not None
    assert dossier.identite.societaire_id == "SOC-1"
    assert dossier.activite.secteur == "Commerce et services"
    assert dossier.epargne.tendance_12m == "hausse"
    assert len(dossier.historique_credit) == 1
    assert dossier.groupe is not None
    assert dossier.alertes == []
