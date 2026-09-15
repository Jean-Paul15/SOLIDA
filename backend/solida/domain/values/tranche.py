from enum import StrEnum


class TrancheDecision(StrEnum):
    """Tranche de la grille de décision. Valeurs alignées sur le contrat frontend.

    Le comité de crédit valide chaque tranche (voir
    `03-MODELE/11-formule-cible-credit-progressif.md`) : ce n'est donc pas une tranche à
    part, mais une étape de gouvernance commune aux trois tranches vivantes ci-dessous.
    """

    ACCORD = "accord"
    ACCORD_SOUS_CONDITION = "accord_sous_condition"
    REFUS = "refus"
    COMITE_DE_CREDIT = "comite_de_credit"
    """Historique uniquement : `decider()` ne la produit plus depuis le passage à 3 tranches
    (l'ancienne zone d'examen est fusionnée dans REFUS). Conservée pour que les décisions
    déjà persistées avec cette tranche restent lisibles — `decision_scoring` est en
    insertion seule (trigger `empecher_modification_decision_scoring`), impossible à
    réécrire rétroactivement."""
