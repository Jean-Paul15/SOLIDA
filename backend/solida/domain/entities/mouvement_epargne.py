from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MouvementEpargne:
    mouvement_id: str
    compte_id: str
    date_operation: date
    sens: str
    """`depot` | `retrait`."""
    montant: int
    type_operation: str
    """depot | retrait | transfert_nantie | restitution_nantie (plus fin que sens)."""
