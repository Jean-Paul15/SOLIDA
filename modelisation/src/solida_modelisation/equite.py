"""Rapports de performance et d'équité, séparés de la matrice de prédiction."""

from __future__ import annotations

import numpy as np
import pandas as pd


def rapport_par_strate(predictions: pd.DataFrame) -> pd.DataFrame:
    """Agrège les probabilités et défauts par strates de revue humaine."""
    dimensions = [
        "zone_residence",
        "numero_cycle",
        "segment_audit",
        "tranche_montant_audit",
    ]
    rapports: list[pd.DataFrame] = []
    for dimension in dimensions:
        if dimension not in predictions:
            continue
        agregat = (
            predictions.groupby(dimension, dropna=False, observed=False)
            .agg(nombre=("cible", "size"), taux_defaut=("cible", "mean"),
                 probabilite_moyenne=("probabilite_defaut", "mean"))
            .reset_index()
            .rename(columns={dimension: "modalite"})
        )
        agregat.insert(0, "dimension", dimension)
        rapports.append(agregat)
    return pd.concat(rapports, ignore_index=True) if rapports else pd.DataFrame()


def ecarts_a_risque_comparable(predictions: pd.DataFrame) -> pd.DataFrame:
    """Mesure les écarts de score par sexe et zone dans chaque décile de risque.

    Aucun seuil d'approbation n'est appliqué ici : ce choix métier est différé.
    Les résultats servent à la revue humaine de la variable zone et à contrôler que
    le sexe, exclu de X, ne reçoit pas une différence systématique inexpliquée.
    """
    resultat = predictions.copy()
    try:
        resultat["decile_risque"] = pd.qcut(
            resultat["probabilite_defaut"], q=10, duplicates="drop"
        ).astype(str)
    except ValueError:
        resultat["decile_risque"] = "unique"
    rapports: list[pd.DataFrame] = []
    for dimension in ("sexe_audit", "zone_residence"):
        if dimension not in resultat:
            continue
        agregat = (
            resultat.groupby(["decile_risque", dimension], dropna=False, observed=False)
            .agg(nombre=("cible", "size"), probabilite_moyenne=("probabilite_defaut", "mean"))
            .reset_index()
            .rename(columns={dimension: "modalite"})
        )
        ecarts = agregat.groupby("decile_risque")["probabilite_moyenne"].transform(
            lambda valeurs: valeurs - valeurs.mean()
        )
        agregat["ecart_probabilite_dans_decile"] = ecarts
        agregat.insert(0, "dimension", dimension)
        rapports.append(agregat)
    return pd.concat(rapports, ignore_index=True) if rapports else pd.DataFrame()


def seuil_revue_humaine(ecarts: pd.DataFrame, seuil: float = 0.05) -> bool:
    """Signale un écart supérieur à cinq points, sans supprimer de variable."""
    if ecarts.empty:
        return False
    return bool(np.abs(ecarts["ecart_probabilite_dans_decile"]).max() > seuil)
