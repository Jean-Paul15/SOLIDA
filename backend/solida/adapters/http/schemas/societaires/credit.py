from typing import Literal

from pydantic import BaseModel

StatutCredit = Literal["en_cours", "solde", "en_souffrance", "radie", "restructure"]


class CreditResume(BaseModel):
    credit_id: str
    produit_id: str
    date_deblocage: str
    montant_octroye: int
    duree_mois: int
    numero_cycle: int
    statut: StatutCredit
    capital_restant_du: int
    max_jours_retard: int
