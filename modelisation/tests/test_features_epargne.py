from datetime import date

from solida_modelisation.features_epargne import SoldeMensuelEpargne, calculer_features_epargne


def _serie(nb_mois: int, depart: float, pas: float, depots_tous: bool = True) -> list[SoldeMensuelEpargne]:
    return [
        SoldeMensuelEpargne(
            mois=date(2024, 1 + i, 1) if i < 12 else date(2025, 1 + (i - 12), 1),
            solde_fin_mois=depart + i * pas,
            total_depots=10_000 if depots_tous else 0,
        )
        for i in range(nb_mois)
    ]


def test_mois_de_reference_et_futurs_sont_exclus() -> None:
    soldes = _serie(15, 0, 10_000)
    resultat = calculer_features_epargne(soldes, date(2025, 3, 1))
    # Mois clos avant 2025-03-01 : jan24..fev25 (indices 0..13) ; les 6 derniers sont
    # indices 8..13, valeurs 80000..130000.
    assert resultat.solde_epargne_moyen_6m == sum(80_000 + i * 10_000 for i in range(6)) / 6
    # Vérifie surtout que le mois >= référence (indice 14) n'entre jamais dans le calcul.
    soldes_futurs_modifies = list(soldes)
    soldes_futurs_modifies[14] = SoldeMensuelEpargne(date(2025, 3, 1), 9_999_999, 10_000)
    resultat_inchange = calculer_features_epargne(soldes_futurs_modifies, date(2025, 3, 1))
    assert resultat_inchange == resultat


def test_moyenne_6_mois_sur_historique_court() -> None:
    soldes = _serie(3, 10_000, 5_000)  # 3 mois clos seulement
    resultat = calculer_features_epargne(soldes, date(2024, 4, 1))
    assert resultat.solde_epargne_moyen_6m == (10_000 + 15_000 + 20_000) / 3


def test_aucun_historique_renvoie_des_valeurs_neutres() -> None:
    resultat = calculer_features_epargne([], date(2024, 1, 1))
    assert resultat.solde_epargne_moyen_6m == 0.0
    assert resultat.nb_mois_avec_depot_12m == 0
    assert resultat.tendance_epargne_12m == "stable"
    assert resultat.volatilite_epargne == 0.0


def test_regularite_compte_les_mois_avec_depot_sur_12_mois() -> None:
    soldes = _serie(12, 0, 1_000, depots_tous=False)
    resultat = calculer_features_epargne(soldes, date(2025, 1, 1))
    assert resultat.nb_mois_avec_depot_12m == 0

    soldes_avec_depots = _serie(12, 0, 1_000, depots_tous=True)
    resultat_avec_depots = calculer_features_epargne(soldes_avec_depots, date(2025, 1, 1))
    assert resultat_avec_depots.nb_mois_avec_depot_12m == 12


def test_tendance_hausse_stable_erosion() -> None:
    hausse = calculer_features_epargne(_serie(12, 100_000, 5_000), date(2025, 1, 1))
    assert hausse.tendance_epargne_12m == "hausse"

    stable = calculer_features_epargne(_serie(12, 100_000, 0), date(2025, 1, 1))
    assert stable.tendance_epargne_12m == "stable"

    erosion = calculer_features_epargne(_serie(12, 100_000, -1_000), date(2025, 1, 1))
    assert erosion.tendance_epargne_12m == "erosion"


def test_mois_non_premier_jour_est_normalise() -> None:
    soldes = [
        SoldeMensuelEpargne(date(2024, 1, 15), 10_000, 5_000),
        SoldeMensuelEpargne(date(2024, 2, 28), 20_000, 5_000),
    ]
    resultat = calculer_features_epargne(soldes, date(2024, 3, 1))
    assert resultat.solde_epargne_moyen_6m == 15_000
