"""Trajectoire d'épargne : fonctions pures partagées entre entraînement et inférence.

Comme `features_groupe.py` pour la couche solidaire, ce module ne dépend pas de pandas afin
d'être importé tel quel côté backend — la parité entraînement/inférence tient à l'identité du
code, pas à une réimplémentation surveillée (J2-11 : le backend recalculait auparavant ces
mêmes statistiques en rejouant les mouvements bruts avec sa propre logique de filtrage,
différente de celle-ci).
"""

from dataclasses import dataclass
from datetime import date

SEUIL_HAUSSE = 0.10
SEUIL_EROSION = -0.05


@dataclass(frozen=True)
class SoldeMensuelEpargne:
    mois: date
    """N'importe quel jour du mois concerné : ramené au premier jour avant comparaison."""
    solde_fin_mois: float
    total_depots: float
    total_retraits: float = 0.0
    """Ignoré par `calculer_features_epargne` ; porté ici pour que le même enregistrement
    serve aussi l'affichage de la trajectoire d'épargne côté backend (J2-11)."""


@dataclass(frozen=True)
class FeaturesEpargne:
    solde_epargne_moyen_6m: float
    nb_mois_avec_depot_12m: int
    tendance_epargne_12m: str
    """`hausse` | `stable` | `erosion`."""
    volatilite_epargne: float


def _premier_jour_mois(valeur: date) -> date:
    return valeur.replace(day=1)


def tendance_depuis_croissance(croissance: float) -> str:
    if croissance > SEUIL_HAUSSE:
        return "hausse"
    if croissance < SEUIL_EROSION:
        return "erosion"
    return "stable"


def calculer_features_epargne(
    soldes: list[SoldeMensuelEpargne], date_reference: date
) -> FeaturesEpargne:
    """Utilise seulement les mois totalement clos avant `date_reference`.

    `soldes` n'a pas besoin d'être trié ni pré-filtré par l'appelant : c'est cette fonction,
    seule, qui décide ce qui est observable à la référence.
    """
    debut_mois_reference = _premier_jour_mois(date_reference)
    historiques = sorted(
        (s for s in soldes if _premier_jour_mois(s.mois) < debut_mois_reference),
        key=lambda s: s.mois,
    )
    derniers_6 = historiques[-6:]
    derniers_12 = historiques[-12:]
    valeurs_6 = [s.solde_fin_mois for s in derniers_6]
    valeurs_12 = [s.solde_fin_mois for s in derniers_12]

    moyenne_6 = sum(valeurs_6) / len(valeurs_6) if valeurs_6 else 0.0
    depots = sum(1 for s in derniers_12 if s.total_depots > 0)
    point_depart = valeurs_12[0] if len(valeurs_12) >= 12 else 0.0
    dernier_solde = valeurs_12[-1] if valeurs_12 else 0.0
    croissance = (dernier_solde - point_depart) / max(abs(point_depart), 1_000.0)

    if valeurs_12:
        variations = [b - a for a, b in zip([0.0, *valeurs_12], valeurs_12, strict=False)]
        moyenne_variations = sum(variations) / len(variations)
        ecart_type = (
            sum((v - moyenne_variations) ** 2 for v in variations) / len(variations)
        ) ** 0.5
        moyenne_solde = sum(valeurs_12) / len(valeurs_12)
        volatilite = ecart_type / max(moyenne_solde, 1.0)
    else:
        volatilite = 0.0

    return FeaturesEpargne(
        solde_epargne_moyen_6m=moyenne_6,
        nb_mois_avec_depot_12m=depots,
        tendance_epargne_12m=tendance_depuis_croissance(croissance),
        volatilite_epargne=volatilite,
    )
