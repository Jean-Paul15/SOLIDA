from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Credit:
    credit_id: str
    societaire_id: str
    produit_id: str
    date_deblocage: date
    date_echeance_prevue: date
    duree_mois: int
    numero_cycle: int
    montant_octroye: int
    statut: str
    """`en_cours` | `solde` | `en_souffrance`."""
    jours_retard_max: int | None
    """`None` pour un crédit en cours : aucun retard observé n'est différent
    d'aucune observation."""
    capital_restant_du: int
