from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreditResume:
    credit_id: str
    produit_id: str
    date_deblocage: date
    montant_octroye: int
    duree_mois: int
    numero_cycle: int
    statut: str
    capital_restant_du: int
    max_jours_retard: int
