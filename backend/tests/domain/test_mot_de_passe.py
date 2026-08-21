import pytest

from solida.domain.errors import MotDePasseInvalide
from solida.domain.rules.mot_de_passe import valider_mot_de_passe

COURANTS = frozenset({"password", "123456"})


def test_un_mot_de_passe_conforme_ne_leve_rien() -> None:
    valider_mot_de_passe("un-mot-de-passe-solide", COURANTS)


def test_un_mot_de_passe_trop_court_est_refuse() -> None:
    with pytest.raises(MotDePasseInvalide):
        valider_mot_de_passe("court12", COURANTS)


def test_un_mot_de_passe_trop_long_est_refuse() -> None:
    with pytest.raises(MotDePasseInvalide):
        valider_mot_de_passe("a" * 65, COURANTS)


def test_un_mot_de_passe_courant_est_refuse() -> None:
    with pytest.raises(MotDePasseInvalide):
        valider_mot_de_passe("password", COURANTS)


def test_la_comparaison_a_la_liste_courante_ignore_la_casse() -> None:
    with pytest.raises(MotDePasseInvalide):
        valider_mot_de_passe("PaSsWoRd", COURANTS)
