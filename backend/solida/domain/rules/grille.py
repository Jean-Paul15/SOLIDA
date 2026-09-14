from dataclasses import dataclass

from solida.domain.errors import GrilleInvalide
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.domain.values.tranche import TrancheDecision


@dataclass(frozen=True)
class ParametresGrille:
    """Seuils de la grille, fondés sur la matrice de coûts — voir docs/formules/."""

    marge: float
    lgd: float
    multiplicateur_accord: float = 0.6
    multiplicateur_vigilance: float = 1.0
    multiplicateur_examen: float = 1.6
    plafond_institutionnel_fcfa: int = 100_000_000
    """Maximum institutionnel unique, sans plafond par produit — décision terrain déjà
    actée (`docs/continuite/2026-09-13-constat-claude-plafonds.md`). Modifiable par la
    supervision via `/parametrage/grille`, pas une constante applicative figée."""
    ratio_endettement_maximal: float = 0.33
    """Part maximale du revenu mensuel que la mensualité d'un nouveau crédit peut
    représenter. Sourcé (2026-09-14, trouvé après coup — la valeur avait d'abord été posée
    en pure démonstration) : étude de terrain CEF-MF Lomé 2025 citée dans
    `PLAN 72H/SOLIDA_Complements_et_Strategie.md` §1.2 — ratio mensualité/revenu moyen de
    23 % sur l'échantillon, rupture identifiée à 33 % au-delà de laquelle le risque d'impayé
    augmente. Ni FUCEC-Togo (page publique des crédits, aucun ratio chiffré) ni le dispositif
    prudentiel BCEAO/UMOA (encadre le taux d'usure, pas un ratio d'endettement individuel) ne
    donnent ce chiffre : c'est une étude d'un autre réseau togolais, à faire confirmer par le
    comité de crédit de la coopérative elle-même avant de la considérer définitive. Seule
    valeur d'endettement du système (voir `progressif_reexamen.py`) ; modifiable sans
    déploiement via `/parametrage/grille` (voir
    PLAN 72H/DECISION_MANQUANTE_ratio_endettement.md)."""

    def __post_init__(self) -> None:
        if self.marge <= 0 or self.lgd <= 0:
            raise GrilleInvalide(
                "La marge et la perte en cas de défaut (LGD) doivent être positives."
            )
        croissants = (
            self.multiplicateur_accord < self.multiplicateur_vigilance < self.multiplicateur_examen
        )
        if not croissants:
            raise GrilleInvalide("Les multiplicateurs de zone doivent être strictement croissants.")
        if self.plafond_institutionnel_fcfa <= 0:
            raise GrilleInvalide("Le plafond institutionnel doit être positif.")
        if not (0 < self.ratio_endettement_maximal <= 1):
            raise GrilleInvalide("Le ratio d'endettement maximal doit être compris entre 0 et 1.")

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
