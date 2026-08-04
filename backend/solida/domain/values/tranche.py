from enum import StrEnum


class TrancheDecision(StrEnum):
    """Tranche de la grille de decision. Valeurs alignees sur le contrat frontend."""

    ACCORD = "accord"
    ACCORD_SOUS_CONDITION = "accord_sous_condition"
    COMITE_DE_CREDIT = "comite_de_credit"
    REFUS = "refus"
