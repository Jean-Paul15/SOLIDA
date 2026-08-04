from dataclasses import dataclass

from solida.domain.values.montant import Montant
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.probabilite import ProbabiliteDefaut


@dataclass(frozen=True)
class ParametresProgressif:
    """Réglage du crédit progressif. Point de départ issu de `simulateur/decision.py`,
    pas une vérité figée."""

    coefficient_progression: float
    montant_plancher: Montant
    plafond_produit: Montant
    plafond_primo_emprunteur: Montant
    modulation_base: float = 1.3
    modulation_pente: float = 2.0
    modulation_min: float = 0.4
    modulation_max: float = 1.2


def calculer_plafond(
    montant_max_rembourse: Montant | None,
    montant_demande: Montant,
    probabilite: ProbabiliteDefaut,
    parametres: ParametresProgressif,
) -> Montant:
    """Borne le montant recommandé par le principe du crédit progressif.

    `montant_max_rembourse` à None signifie un primo-emprunteur (aucun crédit
    antérieur) : le plafond applique alors `plafond_primo_emprunteur`, pas la
    formule générale qui n'a pas de base historique à partir de laquelle progresser.
    """
    plafond: float
    if montant_max_rembourse is None:
        plafond = min(parametres.plafond_primo_emprunteur.valeur, montant_demande.valeur)
    else:
        base = max(
            montant_max_rembourse.valeur * parametres.coefficient_progression,
            parametres.montant_plancher.valeur,
        )
        modulation = min(
            max(
                parametres.modulation_base - parametres.modulation_pente * probabilite.valeur,
                parametres.modulation_min,
            ),
            parametres.modulation_max,
        )
        plafond = min(
            base * modulation,
            parametres.plafond_produit.valeur,
            montant_demande.valeur,
        )

    montant_recommande = max(plafond, parametres.montant_plancher.valeur)
    return Montant(valeur=int(round(montant_recommande)))


@dataclass(frozen=True)
class SituationReexamen:
    """Snapshot des leviers observables pour un dossier qui n'est pas un accord simple."""

    regularite_epargne: float
    ratio_garantie: float
    endettement: float
    tendance_epargne_baissiere: bool
    caution_deja_appelee: bool
    montant_demande: Montant


@dataclass(frozen=True)
class ParametresReexamen:
    """Cibles utilisées pour transformer un refus en parcours d'éligibilité."""

    regularite_cible: float = 0.75
    mois_observation: int = 3
    ratio_garantie_cible: float = 0.5
    endettement_seuil: float = 0.5


def lister_conditions_reexamen(
    situation: SituationReexamen, parametres: ParametresReexamen
) -> list[str]:
    """Leviers concrets et vérifiables que le sociétaire peut activer.

    Le refus cesse d'être une porte fermée : il devient un parcours d'éligibilité.
    """
    conditions: list[str] = []

    if situation.regularite_epargne < parametres.regularite_cible:
        mois_a_rattraper = round((parametres.regularite_cible - situation.regularite_epargne) * 12)
        conditions.append(
            f"Effectuer un dépôt chaque mois pendant {parametres.mois_observation} mois "
            f"(régularité actuelle {situation.regularite_epargne * 100:.0f}%, cible "
            f"{parametres.regularite_cible * 100:.0f}%, soit environ {mois_a_rattraper} mois de "
            "dépôt à rattraper)."
        )

    if situation.ratio_garantie < parametres.ratio_garantie_cible:
        cible = round(situation.montant_demande.valeur * parametres.ratio_garantie_cible)
        conditions.append(
            f"Porter l'épargne nantie à {cible:,} FCFA ".replace(",", " ")
            + f"({parametres.ratio_garantie_cible * 100:.0f}% du montant demandé) pour renforcer "
            "la garantie."
        )

    if situation.endettement > parametres.endettement_seuil:
        conditions.append(
            "Réduire le montant demandé ou allonger la durée : la charge de remboursement "
            f"dépasse {parametres.endettement_seuil * 100:.0f}% du revenu estimé."
        )

    if situation.tendance_epargne_baissiere:
        conditions.append(
            "Stabiliser le solde d'épargne : la trajectoire est orientée à la baisse sur les "
            "12 derniers mois."
        )

    if situation.caution_deja_appelee:
        conditions.append(
            "Régulariser la situation vis-à-vis du groupe : une caution a déjà été appelée "
            "pour ce membre."
        )

    if not conditions:
        conditions.append(
            "Aucun levier bloquant : le dossier peut être réexaminé dès le prochain cycle."
        )

    return conditions


def calculer_trajectoire(
    plafond_actuel: Montant, parametres: ParametresProgressif, nb_cycles: int = 3
) -> list[PalierProgression]:
    """Trajectoire indicative si le sociétaire rembourse sans incident.

    Simplification assumée (identique à `simulateur/decision.py`) : la progression
    future ne remodule pas par le risque à chaque cycle, elle applique le seul
    coefficient de progression borné par le plafond produit. C'est une incitation
    affichée, pas une décision prise à l'avance.
    """
    trajectoire = []
    plafond: float = plafond_actuel.valeur
    for cycle in range(1, nb_cycles + 1):
        plafond = min(
            plafond * parametres.coefficient_progression, parametres.plafond_produit.valeur
        )
        trajectoire.append(
            PalierProgression(cycle=cycle, plafond_accessible=Montant(valeur=int(round(plafond))))
        )
    return trajectoire
