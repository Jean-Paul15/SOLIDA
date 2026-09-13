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
    type_operation: str = "depot"
    """Nature source : dépôt libre, retrait, transfert nanti ou restitution."""
