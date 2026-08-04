from dataclasses import dataclass

from solida.domain.values.montant import Montant
from solida.domain.values.palier_progression import PalierProgression
from solida.domain.values.probabilite import ProbabiliteDefaut


@dataclass(frozen=True)
class ParametresProgressif:
    """Reglage du credit progressif. Point de depart issu de `simulateur/decision.py`,
    pas une verite figee : voir 03-MODELE/03-scorecard-et-grille.md."""

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
    """Borne le montant recommande par le principe du credit progressif.

    `montant_max_rembourse` a None signifie un primo-emprunteur (aucun credit
    anterieur) : le plafond applique alors `plafond_primo_emprunteur`, pas la
    formule generale qui n'a pas de base historique a partir de laquelle progresser.
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
    """Cibles utilisees pour transformer un refus en parcours d'eligibilite."""

    regularite_cible: float = 0.75
    mois_observation: int = 3
    ratio_garantie_cible: float = 0.5
    endettement_seuil: float = 0.5


def lister_conditions_reexamen(
    situation: SituationReexamen, parametres: ParametresReexamen
) -> list[str]:
    """Leviers concrets et verifiables que le societaire peut activer.

    Le refus cesse d'etre une porte fermee : il devient un parcours d'eligibilite.
    Voir 03-MODELE/03-scorecard-et-grille.md, "Au-dela du refus".
    """
    conditions: list[str] = []

    if situation.regularite_epargne < parametres.regularite_cible:
        mois_a_rattraper = round((parametres.regularite_cible - situation.regularite_epargne) * 12)
        conditions.append(
            f"Effectuer un depot chaque mois pendant {parametres.mois_observation} mois "
            f"(regularite actuelle {situation.regularite_epargne * 100:.0f}%, cible "
            f"{parametres.regularite_cible * 100:.0f}%, soit environ {mois_a_rattraper} mois de "
            "depot a rattraper)."
        )

    if situation.ratio_garantie < parametres.ratio_garantie_cible:
        cible = round(situation.montant_demande.valeur * parametres.ratio_garantie_cible)
        conditions.append(
            f"Porter l'epargne nantie a {cible:,} FCFA ".replace(",", " ")
            + f"({parametres.ratio_garantie_cible * 100:.0f}% du montant demande) pour renforcer "
            "la garantie."
        )

    if situation.endettement > parametres.endettement_seuil:
        conditions.append(
            "Reduire le montant demande ou allonger la duree : la charge de remboursement "
            f"depasse {parametres.endettement_seuil * 100:.0f}% du revenu estime."
        )

    if situation.tendance_epargne_baissiere:
        conditions.append(
            "Stabiliser le solde d'epargne : la trajectoire est orientee a la baisse sur les "
            "12 derniers mois."
        )

    if situation.caution_deja_appelee:
        conditions.append(
            "Regulariser la situation vis-a-vis du groupe : une caution a deja ete appelee "
            "pour ce membre."
        )

    if not conditions:
        conditions.append(
            "Aucun levier bloquant : le dossier peut etre reexamine des le prochain cycle."
        )

    return conditions


def calculer_trajectoire(
    plafond_actuel: Montant, parametres: ParametresProgressif, nb_cycles: int = 3
) -> list[PalierProgression]:
    """Trajectoire indicative si le societaire rembourse sans incident.

    Simplification assumee (identique a `simulateur/decision.py`) : la progression
    future ne remodule pas par le risque a chaque cycle, elle applique le seul
    coefficient de progression borne par le plafond produit. C'est une incitation
    affichee, pas une decision prise a l'avance.
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
