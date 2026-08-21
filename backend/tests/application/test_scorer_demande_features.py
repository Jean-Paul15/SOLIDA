import pytest

from solida.application.use_cases.scorer_demande_features import (
    _actualiser_features,
    _features_to_dict,
    _revenu_effectif,
)
from solida.domain.values.demande import ActualisationSituation, DemandeScoring
from solida.domain.values.features import FeaturesIndividuelles


def _demande(**overrides: object) -> DemandeScoring:
    valeurs: dict[str, object] = {
        "societaire_id": "SOC-1",
        "produit_id": "PROD-1",
        "montant_demande": 200000,
        "duree_demandee_mois": 12,
        "objet_credit": "tresorerie",
        "groupe_id": None,
        "actualisation": None,
    }
    valeurs.update(overrides)
    return DemandeScoring(**valeurs)  # type: ignore[arg-type]


def _features_individuelles(**overrides: object) -> FeaturesIndividuelles:
    valeurs: dict[str, object] = {
        "anciennete_societaire_mois": 48,
        "segment": "individuel",
        "solde_epargne_moyen_6m": 100000,
        "nb_mois_avec_depot_12m": 10,
        "tendance_epargne_12m": "hausse",
        "volatilite_epargne": 0.1,
        "ratio_epargne_revenu": 0.5,
        "ratio_epargne_montant": 0.3,
        "anciennete_epargne_mois": 48,
        "ratio_endettement": 0.2,
        "nb_credits_anterieurs": 2,
        "nb_incidents_anterieurs": 0,
        "max_jours_retard_historique": 0,
        "montant_max_rembourse": 150000,
        "numero_cycle": 2,
        "parts_sociales_montant": 10000,
        "nb_personnes_a_charge": 2,
    }
    valeurs.update(overrides)
    return FeaturesIndividuelles(**valeurs)  # type: ignore[arg-type]


# --- _revenu_effectif ---


def test_revenu_effectif_utilise_le_revenu_actualise_si_present() -> None:
    demande = _demande(actualisation=ActualisationSituation(revenu_mensuel_declare=200000))

    assert _revenu_effectif(demande, 100000) == 200000


def test_revenu_effectif_retombe_sur_le_revenu_declare_sans_actualisation() -> None:
    assert _revenu_effectif(_demande(actualisation=None), 100000) == 100000


def test_revenu_effectif_est_nul_si_aucun_revenu_connu() -> None:
    assert _revenu_effectif(_demande(actualisation=None), None) == 0


# --- _actualiser_features ---


def test_actualiser_features_recalcule_les_ratios_dependant_de_la_demande() -> None:
    features = _features_individuelles(solde_epargne_moyen_6m=100000)
    demande = _demande(montant_demande=200000, duree_demandee_mois=12)

    actualisees = _actualiser_features(features, demande, revenu_effectif=150000)

    assert actualisees.ratio_epargne_montant == pytest.approx(min(100000 / 200000, 3.0))
    assert actualisees.ratio_epargne_revenu == pytest.approx(min(100000 / 150000, 5.0))
    assert actualisees.ratio_endettement > 0


def test_actualiser_features_utilise_les_charges_et_personnes_a_charge_actualisees() -> None:
    features = _features_individuelles(nb_personnes_a_charge=1)
    demande = _demande(
        actualisation=ActualisationSituation(charges_mensuelles=20000, nb_personnes_a_charge=4)
    )

    actualisees = _actualiser_features(features, demande, revenu_effectif=150000)

    assert actualisees.nb_personnes_a_charge == 4


# --- _features_to_dict ---


def test_features_to_dict_omet_les_champs_none() -> None:
    features = _features_individuelles(max_jours_retard_historique=None, montant_max_rembourse=None)

    valeurs = _features_to_dict(features, en_groupe=False)

    assert "max_jours_retard_historique" not in valeurs
    assert "montant_max_rembourse" not in valeurs
    assert valeurs["en_groupe"] == 0.0


def test_features_to_dict_marque_en_groupe() -> None:
    valeurs = _features_to_dict(_features_individuelles(), en_groupe=True)

    assert valeurs["en_groupe"] == 1.0
