import math

import pytest

from solida.domain.errors import InvariantScoreViole
from solida.domain.rules.scorecard import (
    ParametresScorecard,
    calculer_score,
    decomposer_en_points,
    verifier_invariant_decomposition,
)
from solida.domain.values.points_variable import PointsVariable
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.domain.values.score import Score

PARAMETRES = ParametresScorecard(
    pdo=20, score_reference=600, odds_reference=50, score_min=300, score_max=850
)


def test_a_la_probabilite_de_reference_le_score_vaut_le_score_de_reference() -> None:
    p_reference = 1 / (1 + PARAMETRES.odds_reference)

    score = calculer_score(ProbabiliteDefaut(p_reference), PARAMETRES)

    assert score.valeur == pytest.approx(PARAMETRES.score_reference, abs=1e-9)


def test_une_probabilite_tres_faible_est_bornee_au_score_max() -> None:
    score = calculer_score(ProbabiliteDefaut(1e-9), PARAMETRES)

    assert score.valeur == PARAMETRES.score_max


def test_une_probabilite_tres_elevee_est_bornee_au_score_min() -> None:
    score = calculer_score(ProbabiliteDefaut(1 - 1e-9), PARAMETRES)

    assert score.valeur == PARAMETRES.score_min


def test_une_probabilite_hors_bornes_leve_une_erreur() -> None:
    with pytest.raises(ValueError):
        ProbabiliteDefaut(0.0)
    with pytest.raises(ValueError):
        ProbabiliteDefaut(1.0)
    with pytest.raises(ValueError):
        ProbabiliteDefaut(1.5)


def test_decomposer_sans_contribution_donne_des_points_de_base_egaux_au_score() -> None:
    p_reference = 1 / (1 + PARAMETRES.odds_reference)
    beta_0 = math.log((1 - p_reference) / p_reference)

    points_de_base, points = decomposer_en_points(beta_0, [], PARAMETRES)

    assert points == []
    assert points_de_base == pytest.approx(PARAMETRES.score_reference, abs=1e-9)


def test_decomposer_avec_contributions_repartit_le_facteur_sur_chaque_variable() -> None:
    points_de_base, points = decomposer_en_points(
        beta_0=0.0,
        contributions_log_odds=[("epargne_reguliere", 0.5), ("anciennete", -0.2)],
        parametres=PARAMETRES,
    )

    facteur = PARAMETRES.facteur()
    assert points == [
        PointsVariable(code_variable="epargne_reguliere", points=facteur * 0.5),
        PointsVariable(code_variable="anciennete", points=facteur * -0.2),
    ]


def test_la_somme_des_points_egale_toujours_le_score() -> None:
    points_de_base = 550.0
    points = [PointsVariable("a", 30.0), PointsVariable("b", -10.0)]
    score = Score(valeur=570.0)

    verifier_invariant_decomposition(points_de_base, points, score)


def test_un_ecart_entre_la_decomposition_et_le_score_leve_invariant_score_viole() -> None:
    points_de_base = 550.0
    points = [PointsVariable("a", 30.0)]
    score = Score(valeur=600.0)

    with pytest.raises(InvariantScoreViole):
        verifier_invariant_decomposition(points_de_base, points, score)
