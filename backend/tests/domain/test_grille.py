import pytest

from solida.domain.errors import GrilleInvalide
from solida.domain.rules.grille import ParametresGrille, decider
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.domain.values.tranche import TrancheDecision

PARAMETRES = ParametresGrille(marge=0.15, lgd=0.75)


def test_le_seuil_economique_est_marge_sur_marge_plus_lgd() -> None:
    assert PARAMETRES.seuil_economique() == pytest.approx(0.15 / 0.9)


def test_une_probabilite_faible_est_un_accord() -> None:
    assert decider(ProbabiliteDefaut(0.05), PARAMETRES) == TrancheDecision.ACCORD


def test_une_probabilite_moderee_est_un_accord_sous_condition() -> None:
    assert decider(ProbabiliteDefaut(0.12), PARAMETRES) == TrancheDecision.ACCORD_SOUS_CONDITION


def test_une_probabilite_au_dela_du_seuil_economique_est_un_refus() -> None:
    assert decider(ProbabiliteDefaut(0.20), PARAMETRES) == TrancheDecision.REFUS


def test_une_probabilite_tres_elevee_est_un_refus() -> None:
    assert decider(ProbabiliteDefaut(0.30), PARAMETRES) == TrancheDecision.REFUS


def test_a_la_frontiere_exacte_la_zone_superieure_est_retenue() -> None:
    seuil = PARAMETRES.seuil_economique()
    frontiere_accord = seuil * PARAMETRES.multiplicateur_accord

    resultat = decider(ProbabiliteDefaut(frontiere_accord), PARAMETRES)

    assert resultat == TrancheDecision.ACCORD_SOUS_CONDITION


def test_une_marge_ou_une_lgd_non_positive_leve_grille_invalide() -> None:
    with pytest.raises(GrilleInvalide):
        ParametresGrille(marge=0.0, lgd=0.75)
    with pytest.raises(GrilleInvalide):
        ParametresGrille(marge=0.15, lgd=0.0)


def test_un_multiplicateur_accord_hors_bornes_leve_grille_invalide() -> None:
    with pytest.raises(GrilleInvalide):
        ParametresGrille(marge=0.15, lgd=0.75, multiplicateur_accord=1.0)
    with pytest.raises(GrilleInvalide):
        ParametresGrille(marge=0.15, lgd=0.75, multiplicateur_accord=0.0)
