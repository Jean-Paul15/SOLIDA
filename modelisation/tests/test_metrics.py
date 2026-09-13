import numpy as np
import pytest

from solida_modelisation.metrics import ecart_maximal_deciles


def test_ecart_maximal_utilise_des_deciles_de_population() -> None:
    probabilites = np.asarray([0.01] * 10 + [0.9] * 10)
    cible = np.asarray([0] * 10 + [1] * 10)

    assert ecart_maximal_deciles(cible, probabilites, bins=2) == pytest.approx(0.1)
