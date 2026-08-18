from pydantic import BaseModel

from solida.adapters.http.schemas.societaires.credit import CreditResume
from solida.adapters.http.schemas.societaires.epargne import SyntheseEpargne
from solida.adapters.http.schemas.societaires.groupe import SyntheseGroupe
from solida.adapters.http.schemas.societaires.identite import ActiviteEconomique, IdentiteSocietaire


class DossierSocietaire(BaseModel):
    identite: IdentiteSocietaire
    activite: ActiviteEconomique
    epargne: SyntheseEpargne
    historique_credit: list[CreditResume]
    groupe: SyntheseGroupe | None = None
    alertes: list[str]
