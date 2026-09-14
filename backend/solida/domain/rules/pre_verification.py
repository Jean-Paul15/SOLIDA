from dataclasses import dataclass

from solida.domain.values.montant import Montant
from solida.domain.values.tranche import TrancheDecision

# Section 1.7 de SOLIDA_Complements_et_Strategie.md, dupliquee cote backend (la meme
# table existe deja cote frontend-societaire/lib/objets-credit.ts, aucune des deux
# couches ne peut lire l'autre). Objets hors table 1.7 -> "mixte" par prudence
# (jamais devine divisible), memes choix que le frontend.
DIVISIBLE = "divisible"
INDIVISIBLE = "indivisible"
MIXTE = "mixte"

DIVISIBILITE_OBJET = {
    "fonds_roulement": DIVISIBLE,
    "stock": DIVISIBLE,
    "intrants_agricoles": DIVISIBLE,
    "equipement": INDIVISIBLE,
    "urgence_sante": MIXTE,
    "scolarite": MIXTE,
    "habitat": MIXTE,
    "autre": MIXTE,
}

ISSUE_PEUT_AVANCER = "peut_avancer"
ISSUE_MONTANT_REDUIT = "montant_reduit"
ISSUE_DUREE_OU_ATTENTE = "duree_ou_attente"
ISSUE_PAS_MAINTENANT = "pas_maintenant"

MESSAGE_PEUT_AVANCER = (
    "D'après ce que votre caisse sait de vous, votre demande peut avancer. "
    "Votre agent va la regarder et vous recontacter."
)
MESSAGE_DUREE_OU_ATTENTE = (
    "Le montant que vous demandez pour cet achat est encore difficile pour vous "
    "aujourd'hui. Deux possibilités : allonger un peu la durée pour réduire ce que "
    "vous payez chaque mois, ou patienter un cycle de remboursement pour renforcer "
    "votre dossier. Votre agent peut voir avec vous laquelle vous convient."
)


@dataclass(frozen=True)
class PreVerification:
    issue: str
    message: str
    montant_propose: int | None


def calculer_pre_verification(
    tranche: TrancheDecision,
    montant_demande: Montant,
    montant_recommande: Montant,
    objet_credit: str,
    conditions_reexamen: list[str],
) -> PreVerification:
    if tranche == TrancheDecision.REFUS:
        suite = " ".join(conditions_reexamen) if conditions_reexamen else ""
        message = (
            "Aujourd'hui, cette demande serait difficile à rembourser pour vous. "
            f"{suite} Votre agent peut en discuter avec vous."
        ).strip()
        return PreVerification(ISSUE_PAS_MAINTENANT, message, None)

    if tranche == TrancheDecision.ACCORD and montant_recommande.valeur >= montant_demande.valeur:
        return PreVerification(ISSUE_PEUT_AVANCER, MESSAGE_PEUT_AVANCER, None)

    # accord_sous_condition, comite_de_credit, ou accord avec montant reduit :
    # jamais un montant reduit sur un objet indivisible/mixte (section 1.7).
    divisibilite = DIVISIBILITE_OBJET.get(objet_credit, MIXTE)
    if divisibilite == DIVISIBLE and montant_recommande.valeur < montant_demande.valeur:
        message = (
            "Votre demande peut avancer, mais avec un montant plus prudent pour "
            f"commencer : {montant_recommande.valeur:,} francs au lieu de "
            f"{montant_demande.valeur:,}. Si vous remboursez bien celui-ci, le "
            "suivant pourra être plus important."
        ).replace(",", " ")
        return PreVerification(ISSUE_MONTANT_REDUIT, message, montant_recommande.valeur)

    return PreVerification(ISSUE_DUREE_OU_ATTENTE, MESSAGE_DUREE_OU_ATTENTE, None)
