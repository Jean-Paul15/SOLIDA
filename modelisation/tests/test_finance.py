from solida_modelisation.finance import mensualite_actuarielle


def test_mensualite_actuarielle_taux_zero() -> None:
    assert mensualite_actuarielle(120_000, 12, 0.0) == 10_000


def test_mensualite_actuarielle_est_positive() -> None:
    assert mensualite_actuarielle(100_000, 12, 0.14) > 100_000 / 12
