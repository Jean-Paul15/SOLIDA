from solida.adapters.http.schemas.societaires.credit import CreditResume, StatutCredit
from solida.adapters.http.schemas.societaires.dossier import DossierSocietaire
from solida.adapters.http.schemas.societaires.epargne import (
    MouvementEpargne,
    SyntheseEpargne,
    TendanceEpargne,
)
from solida.adapters.http.schemas.societaires.groupe import (
    MembreGroupe,
    RoleGroupe,
    StatutCreditMembre,
    StatutGroupe,
    SyntheseGroupe,
)
from solida.adapters.http.schemas.societaires.identite import (
    ActiviteEconomique,
    IdentiteSocietaire,
    NiveauInstruction,
    Segment,
    SocietaireSearchResult,
    StatutSocietaire,
)

__all__ = [
    "ActiviteEconomique",
    "CreditResume",
    "DossierSocietaire",
    "IdentiteSocietaire",
    "MembreGroupe",
    "MouvementEpargne",
    "NiveauInstruction",
    "RoleGroupe",
    "Segment",
    "SocietaireSearchResult",
    "StatutCredit",
    "StatutCreditMembre",
    "StatutGroupe",
    "StatutSocietaire",
    "SyntheseEpargne",
    "SyntheseGroupe",
    "TendanceEpargne",
]
