import math
from dataclasses import dataclass

from solida.domain.erreurs import InvariantScoreViole
from solida.domain.values.points_variable import PointsVariable
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.domain.values.score import Score

TOLERANCE_INVARIANT = 1.0


@dataclass(frozen=True)
class ParametresScorecard:
    """Mise à l'échelle probabilité de défaut -> score, par transformation PDO."""

    pdo: float
    score_reference: float
    odds_reference: float
    score_min: float
    score_max: float

    def facteur(self) -> float:
        return self.pdo / math.log(2)

    def decalage(self) -> float:
        return self.score_reference - self.facteur() * math.log(self.odds_reference)


def calculer_score(probabilite: ProbabiliteDefaut, parametres: ParametresScorecard) -> Score:
    """Transforme une probabilité de défaut en score.

    Convention bancaire : score élevé = risque faible, donc le rapport est
    (1 - p) / p, pas son inverse. Le résultat est borné à [score_min, score_max].
    """
    log_odds = math.log((1 - probabilite.valeur) / probabilite.valeur)
    score_brut = parametres.decalage() + parametres.facteur() * log_odds
    score_borne = min(max(score_brut, parametres.score_min), parametres.score_max)
    return Score(valeur=score_borne)


def decomposer_en_points(
    beta_0: float,
    contributions_log_odds: list[tuple[str, float]],
    parametres: ParametresScorecard,
) -> tuple[float, list[PointsVariable]]:
    """Répartit un log-odds en points de base et contributions par variable.

    Suppose que `beta_0 + sum(f_j pour f_j dans contributions_log_odds)` est le
    log-odds complet produit par le modèle. La transformation étant affine, chaque
    terme se met à l'échelle indépendamment par le même facteur.
    """
    facteur = parametres.facteur()
    points_de_base = parametres.decalage() + facteur * beta_0
    points = [
        PointsVariable(code_variable=code, points=facteur * valeur)
        for code, valeur in contributions_log_odds
    ]
    return points_de_base, points


def verifier_invariant_decomposition(
    points_de_base: float, points: list[PointsVariable], score: Score
) -> None:
    """Lève InvariantScoreViole si la décomposition ne somme pas au score rendu.

    Une fiche de justification dont les points ne somment pas au score détruirait
    toute la crédibilité du produit devant un auditeur : mieux vaut rejeter le
    scoring que le rendre incohérent.
    """
    somme = points_de_base + sum(p.points for p in points)
    if abs(somme - score.valeur) >= TOLERANCE_INVARIANT:
        raise InvariantScoreViole(
            f"La décomposition en points ({somme:.2f}) ne correspond pas au score "
            f"rendu ({score.valeur:.2f})."
        )
