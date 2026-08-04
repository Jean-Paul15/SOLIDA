from dataclasses import dataclass


@dataclass(frozen=True)
class CompteEpargne:
    compte_id: str
    societaire_id: str
    solde_moyen_6m: int
    nb_mois_avec_depot_12m: int
    croissance_12m: float
    volatilite: float
