from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from solida.domain.rules import jeton_societaire
from solida.domain.rules.jeton_societaire import generer_jeton, verifier_jeton

SECRET = "un-secret-de-test"


def test_un_jeton_valide_renvoie_le_societaire_id() -> None:
    jeton = generer_jeton(SECRET, "SOC-1")
    assert verifier_jeton(SECRET, jeton) == "SOC-1"


def test_un_mauvais_secret_est_rejete() -> None:
    jeton = generer_jeton(SECRET, "SOC-1")
    assert verifier_jeton("autre-secret", jeton) is None


def test_un_jeton_malforme_est_rejete() -> None:
    assert verifier_jeton(SECRET, "ceci-nest-pas-un-jeton") is None


def test_un_jeton_expire_est_rejete() -> None:
    jeton = generer_jeton(SECRET, "SOC-1")
    plus_tard = datetime.now(UTC) + jeton_societaire.DUREE_SESSION + timedelta(minutes=1)
    with patch("solida.domain.rules.jeton_societaire.datetime") as horloge:
        horloge.now.return_value = plus_tard
        assert verifier_jeton(SECRET, jeton) is None
