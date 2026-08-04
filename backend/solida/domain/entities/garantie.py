from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Garantie:
    garantie_id: str
    credit_id: str
    type_garantie: str
    """`caution_solidaire_gie` | `epargne_nantie`."""
    garant_societaire_id: str | None
    beneficiaire_societaire_id: str
    montant_garanti: int
    date_engagement: date
    garantie_appelee: bool
