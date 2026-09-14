from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UtilisateurResume:
    id: str
    nom_complet: str
    role: str
    agence_id: str | None
    desactive_le: datetime | None
