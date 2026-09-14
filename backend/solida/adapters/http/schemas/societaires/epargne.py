from typing import Literal

from pydantic import BaseModel

TendanceEpargne = Literal["hausse", "stable", "erosion"]


class PointSoldeMensuel(BaseModel):
    mois: str
    solde_fin_mois: int
    total_depots: int
    total_retraits: int


class SyntheseEpargne(BaseModel):
    solde_moyen_6m: int
    tendance_12m: TendanceEpargne
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    serie_solde_12m: list[PointSoldeMensuel]
