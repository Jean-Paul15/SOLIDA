from typing import Literal

from pydantic import BaseModel

TendanceEpargne = Literal["hausse", "stable", "erosion"]


class MouvementEpargne(BaseModel):
    date_operation: str
    sens: Literal["depot", "retrait"]
    montant: int


class SyntheseEpargne(BaseModel):
    solde_moyen_6m: int
    tendance_12m: TendanceEpargne
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    mouvements_recents: list[MouvementEpargne]
