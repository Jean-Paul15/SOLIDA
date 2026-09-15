from dataclasses import dataclass

from solida.domain.values.montant import Montant


@dataclass(frozen=True)
class SituationReexamen:
    """Snapshot des leviers observables pour un dossier qui n'est pas un accord simple."""

    regularite_epargne: float
    ratio_garantie: float
    endettement: float | None
    tendance_epargne_baissiere: bool
    caution_deja_appelee: bool
    montant_demande: Montant


@dataclass(frozen=True)
class ParametresReexamen:
    """Cibles utilisées pour transformer un refus en parcours d'éligibilité.

    Pas de seuil d'endettement propre à cette règle : `lister_conditions_reexamen` reçoit
    celui de la grille (`ParametresGrille.ratio_endettement_maximal`, sourcé CEF-MF Lomé
    2025) pour qu'une seule valeur d'endettement existe dans tout le système, modifiable à
    un seul endroit (`/parametrage/grille`).
    """

    regularite_cible: float = 0.75
    mois_observation: int = 3
    ratio_garantie_cible: float = 0.5


def lister_conditions_reexamen(
    situation: SituationReexamen, parametres: ParametresReexamen, endettement_seuil: float
) -> list[str]:
    """Leviers concrets et vérifiables que le sociétaire peut activer.

    Le refus cesse d'être une porte fermée : il devient un parcours d'éligibilité.
    `endettement_seuil` vient de la grille active (`ratio_endettement_maximal`), jamais
    d'une constante propre à cette règle.
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

    if situation.endettement is not None and situation.endettement > endettement_seuil:
        conditions.append(
            "Ramener la charge de remboursement sous "
            f"{endettement_seuil * 100:.0f}% du revenu estimé : c'est le seuil de rupture "
            "actuellement retenu par votre coopérative, ajustable selon son expérience."
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
