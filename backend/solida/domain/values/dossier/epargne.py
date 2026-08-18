from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MouvementEpargneAffiche:
    date_operation: date
    sens: str
    """`depot` | `retrait`."""
    montant: int


@dataclass(frozen=True)
class SyntheseEpargne:
    solde_moyen_6m: int
    tendance_12m: str
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    # Échantillon réel de mouvements récents (pas une courbe de solde reconstruite, voir
    # docs/backend/03-decisions-provisoires-a-revoir.md) : pas une série complète.
    mouvements_recents: list[MouvementEpargneAffiche]
