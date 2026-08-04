import pytest

from solida.domain.values.montant import Montant


def test_un_montant_negatif_leve_une_erreur() -> None:
    with pytest.raises(ValueError):
        Montant(valeur=-1)


def test_un_montant_positif_est_accepte() -> None:
    assert Montant(valeur=0).valeur == 0
    assert Montant(valeur=150_000).valeur == 150_000
