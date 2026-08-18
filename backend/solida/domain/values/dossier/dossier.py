from dataclasses import dataclass

from solida.domain.values.dossier.credit import CreditResume
from solida.domain.values.dossier.epargne import SyntheseEpargne
from solida.domain.values.dossier.groupe import SyntheseGroupe
from solida.domain.values.dossier.identite import ActiviteEconomique, IdentiteSocietaire


@dataclass(frozen=True)
class DossierSocietaire:
    identite: IdentiteSocietaire
    activite: ActiviteEconomique
    epargne: SyntheseEpargne
    historique_credit: list[CreditResume]
    groupe: SyntheseGroupe | None
    alertes: list[str]
