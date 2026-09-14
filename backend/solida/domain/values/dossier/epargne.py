from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PointSoldeMensuel:
    """Un mois réellement arrêté (`solde_mensuel_epargne`) : jamais un point reconstruit ou
    interpolé (J2-11 — voir `PLAN 72H/SOLIDA_Complements_et_Strategie.md` §5.2/5.14)."""

    mois: date
    solde_fin_mois: int
    total_depots: int
    total_retraits: int


@dataclass(frozen=True)
class SyntheseEpargne:
    solde_moyen_6m: int
    tendance_12m: str
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    # Série réelle des soldes de fin de mois (épargne libre), triée chronologiquement, jusqu'à
    # 24 mois. Le front n'a plus à reconstruire quoi que ce soit : `mois_affiches =
    # min(fenêtre_demandée, len(serie))`, jamais complété par des zéros (§5.14).
    serie_solde_12m: list[PointSoldeMensuel]
