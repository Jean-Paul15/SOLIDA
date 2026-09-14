from dataclasses import dataclass, field
from datetime import date

from solida_modelisation.features_epargne import SoldeMensuelEpargne

from solida.adapters.core_sim.feature_store_core_sim import FeatureStoreCoreSim
from solida.domain.entities.credit import Credit
from solida.domain.entities.societaire import Societaire
from solida.domain.values.features import DonneesGroupeBrutes


def _societaire(**overrides: object) -> Societaire:
    values: dict[str, object] = {
        "societaire_id": "SOC-1",
        "numero_membre": "100001",
        "nom_complet": "Test",
        "agence": "CAI-00",
        "date_adhesion": date(2020, 1, 1),
        "anciennete_mois": 48,
        "segment": "individuel",
        "age": 35,
        "zone": "urbain",
        "nb_personnes_a_charge": 2,
        "niveau_instruction": None,
        "parts_sociales_montant": 10_000,
        "revenu_mensuel_declare": 150_000,
        "groupe_id": None,
        "a_credit_en_cours": False,
    }
    values.update(overrides)
    return Societaire(**values)  # type: ignore[arg-type]


@dataclass
class _FakeCoreSimReader:
    societaire: Societaire | None
    soldes: list[SoldeMensuelEpargne] = field(default_factory=list)
    credits: list[Credit] = field(default_factory=list)

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return self.societaire

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        return self.credits

    def charger_soldes_mensuels(self, societaire_id: str, avant: date) -> list[SoldeMensuelEpargne]:
        return [s for s in self.soldes if s.mois <= avant]

    def charger_donnees_groupe(self, gie_id: str) -> DonneesGroupeBrutes | None:
        raise NotImplementedError


def test_lire_individuelles_renvoie_none_si_societaire_introuvable() -> None:
    store = FeatureStoreCoreSim(_FakeCoreSimReader(societaire=None))  # type: ignore[arg-type]
    assert store.lire_individuelles("SOC-1", date(2025, 1, 1)) is None


def test_lire_individuelles_calcule_l_epargne_depuis_les_soldes_mensuels() -> None:
    soldes = [
        SoldeMensuelEpargne(date(2024, m, 1), solde_fin_mois=10_000.0 * m, total_depots=5_000.0)
        for m in range(1, 13)
    ]
    reader = _FakeCoreSimReader(societaire=_societaire(), soldes=soldes)
    store = FeatureStoreCoreSim(reader)  # type: ignore[arg-type]

    features = store.lire_individuelles("SOC-1", date(2025, 1, 1))

    assert features is not None
    # Mêmes 12 mois clos avant 2025-01-01 : les 6 derniers valent 70000..120000 (pas de 10000).
    assert features.solde_epargne_moyen_6m == round(sum(range(70_000, 130_000, 10_000)) / 6)
    assert features.nb_mois_avec_depot_12m == 12
    assert features.tendance_epargne_12m == "hausse"


def test_lire_individuelles_ignore_les_soldes_futurs() -> None:
    soldes = [
        SoldeMensuelEpargne(date(2024, 1, 1), solde_fin_mois=10_000.0, total_depots=5_000.0),
        # Mois de la référence : ne doit jamais influencer le calcul.
        SoldeMensuelEpargne(date(2025, 1, 1), solde_fin_mois=9_999_999.0, total_depots=5_000.0),
    ]
    reader = _FakeCoreSimReader(societaire=_societaire(), soldes=soldes)
    store = FeatureStoreCoreSim(reader)  # type: ignore[arg-type]

    features = store.lire_individuelles("SOC-1", date(2025, 1, 1))

    assert features is not None
    assert features.solde_epargne_moyen_6m == 10_000


def test_lire_individuelles_sans_historique_epargne_renvoie_des_valeurs_neutres() -> None:
    reader = _FakeCoreSimReader(societaire=_societaire(), soldes=[])
    store = FeatureStoreCoreSim(reader)  # type: ignore[arg-type]

    features = store.lire_individuelles("SOC-1", date(2025, 1, 1))

    assert features is not None
    assert features.solde_epargne_moyen_6m == 0
    assert features.nb_mois_avec_depot_12m == 0
    assert features.tendance_epargne_12m == "stable"
    assert features.ratio_epargne_revenu == 0.0
