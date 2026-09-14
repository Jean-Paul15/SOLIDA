import pytest

from solida.domain.rules.capacite_remboursement import montant_maximal_supportable


def test_montant_maximal_croit_avec_le_revenu() -> None:
    petit = montant_maximal_supportable(
        revenu_mensuel=50_000, duree_mois=12, taux_annuel=0.15, ratio_endettement_maximal=0.33
    )
    grand = montant_maximal_supportable(
        revenu_mensuel=200_000, duree_mois=12, taux_annuel=0.15, ratio_endettement_maximal=0.33
    )
    assert grand.valeur > petit.valeur


def test_montant_maximal_a_taux_zero_est_mensualite_fois_duree() -> None:
    resultat = montant_maximal_supportable(
        revenu_mensuel=150_000, duree_mois=10, taux_annuel=0.0, ratio_endettement_maximal=0.5
    )
    # A taux nul, mensualité = montant / durée, donc montant = mensualité_max * durée.
    assert resultat.valeur == pytest.approx(150_000 * 0.5 * 10, rel=1e-9)


def test_montant_maximal_augmente_avec_la_duree() -> None:
    court = montant_maximal_supportable(
        revenu_mensuel=150_000, duree_mois=6, taux_annuel=0.15, ratio_endettement_maximal=0.33
    )
    long_terme = montant_maximal_supportable(
        revenu_mensuel=150_000, duree_mois=24, taux_annuel=0.15, ratio_endettement_maximal=0.33
    )
    assert long_terme.valeur > court.valeur


def test_montant_maximal_avec_revenu_nul_est_zero() -> None:
    resultat = montant_maximal_supportable(
        revenu_mensuel=0, duree_mois=12, taux_annuel=0.15, ratio_endettement_maximal=0.33
    )
    assert resultat.valeur == 0


def test_montant_maximal_respecte_exactement_le_ratio_a_la_reconstitution() -> None:
    from solida_modelisation.finance import mensualite_actuarielle

    resultat = montant_maximal_supportable(
        revenu_mensuel=180_000, duree_mois=18, taux_annuel=0.18, ratio_endettement_maximal=0.33
    )
    mensualite = mensualite_actuarielle(resultat.valeur, 18, 0.18)
    assert mensualite <= 180_000 * 0.33 * 1.01  # tolérance d'arrondi sur le montant entier
