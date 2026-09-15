from collections.abc import Mapping
from dataclasses import dataclass

from solida.domain.values.montant import Montant
from solida.domain.values.tranche import TrancheDecision

# La classification divisible/indivisible/mixte (section 1.7 de
# SOLIDA_Complements_et_Strategie.md) n'a jamais été confirmée comme donnée métier réelle
# (modelisation/docs/decisions-socle.md : « n'existe dans aucune source de référence, ni
# inventée ni utilisée »). Elle vit désormais dans `ConfigurationGrille.classification_objets`
# — versionnée, modifiable par la supervision, vide par défaut. Un objet absent de cette
# table est `NON_CLASSE`, jamais deviné `divisible`.
DIVISIBLE = "divisible"
INDIVISIBLE = "indivisible"
MIXTE = "mixte"
NON_CLASSE = "non_classe"

ISSUE_PEUT_AVANCER = "peut_avancer"
ISSUE_MONTANT_REDUIT = "montant_reduit"
ISSUE_DUREE_OU_ATTENTE = "duree_ou_attente"
ISSUE_PAS_MAINTENANT = "pas_maintenant"
ISSUE_REVUE_OBLIGATOIRE = "revue_obligatoire"

MESSAGE_PEUT_AVANCER = "Votre demande peut avancer. Votre agent va la regarder et vous recontacter."
MESSAGE_DUREE_OU_ATTENTE = (
    "Le montant que vous demandez pour cet achat est encore difficile pour vous "
    "aujourd'hui. Deux possibilités : allonger un peu la durée pour réduire ce que "
    "vous payez chaque mois, ou patienter un cycle de remboursement pour renforcer "
    "votre dossier. Votre agent peut voir avec vous laquelle vous convient."
)
MESSAGE_REVUE_OBLIGATOIRE = (
    "Votre demande a été transmise pour un examen particulier avant toute suite. "
    "Votre agent vous recontactera."
)

OBJET_AUTRE = "autre"
"""Seul objet du catalogue fermé qui ne décrit pas un usage classifié. Un objet "autre"
n'est jamais traité automatiquement (pas de lecture de texte libre, la liste reste fermée) :
il est systématiquement routé vers un examen humain obligatoire (comité de crédit /
conformité) avant toute suite, quelle que soit la tranche produite par le modèle -- la
prévention se fait à la construction du catalogue d'objets (le curer pour qu'il ne contienne
que des usages licites), pas par une détection a posteriori."""


@dataclass(frozen=True)
class PreVerification:
    issue: str
    message: str
    montant_propose: int | None


def classe_objet(objet_credit: str, classification_objets: Mapping[str, str]) -> str:
    """`NON_CLASSE` pour tout objet absent de la table active : jamais deviné depuis le
    libellé (`questionnaire-modele-enrichi.md` : « aucun classement ne sera inféré »)."""
    return classification_objets.get(objet_credit, NON_CLASSE)


def calculer_pre_verification(
    tranche: TrancheDecision,
    montant_demande: Montant,
    montant_recommande: Montant,
    objet_credit: str,
    conditions_reexamen: list[str],
    classification_objets: Mapping[str, str],
) -> PreVerification:
    # Vérifié avant toute autre branche : un objet "autre" est toujours une revue
    # obligatoire, indépendamment de ce que recommande le modèle.
    if objet_credit == OBJET_AUTRE:
        return PreVerification(ISSUE_REVUE_OBLIGATOIRE, MESSAGE_REVUE_OBLIGATOIRE, None)

    if tranche == TrancheDecision.REFUS:
        suite = " ".join(conditions_reexamen) if conditions_reexamen else ""
        message = (
            "Aujourd'hui, cette demande serait difficile à rembourser pour vous. "
            f"{suite} Votre agent peut en discuter avec vous."
        ).strip()
        return PreVerification(ISSUE_PAS_MAINTENANT, message, None)

    if tranche == TrancheDecision.ACCORD and montant_recommande.valeur >= montant_demande.valeur:
        return PreVerification(ISSUE_PEUT_AVANCER, MESSAGE_PEUT_AVANCER, None)

    # accord_sous_condition, ou accord avec montant reduit :
    # jamais un montant reduit sur un objet indivisible, mixte ou non classe (section 1.7).
    divisibilite = classe_objet(objet_credit, classification_objets)
    if divisibilite == DIVISIBLE and montant_recommande.valeur < montant_demande.valeur:
        message = (
            "Votre demande peut avancer, mais avec un montant plus prudent pour "
            f"commencer : {montant_recommande.valeur:,} francs au lieu de "
            f"{montant_demande.valeur:,}. Si vous remboursez bien celui-ci, le "
            "suivant pourra être plus important."
        ).replace(",", " ")
        return PreVerification(ISSUE_MONTANT_REDUIT, message, montant_recommande.valeur)

    return PreVerification(ISSUE_DUREE_OU_ATTENTE, MESSAGE_DUREE_OU_ATTENTE, None)
