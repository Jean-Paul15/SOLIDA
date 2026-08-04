from dataclasses import dataclass

from solida.domain.erreurs import GrilleInvalide
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.domain.values.tranche import TrancheDecision


@dataclass(frozen=True)
class ParametresGrille:
    """Seuils de la grille, fondés sur la matrice de coûts.

    `marge` et `lgd` (perte en cas de défaut) ne sont pas un choix technique : ils
    traduisent l'arbitrage risque/approbation de la coopérative. Les valeurs par
    défaut de `simulateur/decision.py` sont un point de départ, pas la vérité
    finale.
    """

    marge: float
    lgd: float
    multiplicateur_accord: float = 0.6
    multiplicateur_vigilance: float = 1.0
    multiplicateur_examen: float = 1.6

    def __post_init__(self) -> None:
        if self.marge <= 0 or self.lgd <= 0:
            raise GrilleInvalide(
                "La marge et la perte en cas de défaut (LGD) doivent être positives."
            )
        croissants = (
            self.multiplicateur_accord < self.multiplicateur_vigilance < self.multiplicateur_examen
        )
        if not croissants:
            raise GrilleInvalide(
                "Les multiplicateurs de zone doivent être strictement croissants."
            )

    def seuil_economique(self) -> float:
        return self.marge / (self.marge + self.lgd)


def decider(probabilite: ProbabiliteDefaut, parametres: ParametresGrille) -> TrancheDecision:
    """Détermine la tranche à partir du seuil économique marge / (marge + LGD).

    Le seuil se traduit ensuite en score par la même transformation PDO, pour
    rester affichable, mais la décision se prend sur la probabilité.
    """
    seuil = parametres.seuil_economique()
    p = probabilite.valeur
    if p < seuil * parametres.multiplicateur_accord:
        return TrancheDecision.ACCORD
    if p < seuil * parametres.multiplicateur_vigilance:
        return TrancheDecision.ACCORD_SOUS_CONDITION
    if p < seuil * parametres.multiplicateur_examen:
        return TrancheDecision.COMITE_DE_CREDIT
    return TrancheDecision.REFUS
