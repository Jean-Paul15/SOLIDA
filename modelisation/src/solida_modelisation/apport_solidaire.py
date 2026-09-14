"""Mesure de l'apport de la couche solidaire (J2-04).

Compare le modèle enrichi au SOCLE sur la seule population où la couche solidaire peut
jouer un rôle : les crédits de groupe du test. Un sociétaire hors crédit de groupe n'a
aucune variable de groupe (`taille_groupe` absente), donc les deux modèles lui donnent
des prédictions identiques — les inclure diluerait l'écart mesuré vers zéro sans rien
dire de l'apport réel.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .metrics import metriques_classification


@dataclass(frozen=True)
class ApportCoucheSolidaire:
    n_credits: int
    n_defauts: int
    effectif_sous_seuil_fiabilite: bool
    """`True` si l'effectif est sous le seuil de fiabilité terrain (R45, ~8 000 dossiers) :
    le résultat reste indicatif, pas une validation statistique au sens de la coopérative."""
    metriques_socle: dict[str, float]
    metriques_enrichi: dict[str, float]
    delta: dict[str, float]
    """`metriques_enrichi - metriques_socle`, positif = amélioration pour auc/auprc,
    négatif = amélioration pour log_loss/brier/ece/ecart_max_decile."""
    intervalle_confiance_95: dict[str, tuple[float, float]]


SEUIL_FIABILITE_STATISTIQUE_R45 = 8_000


def _population_credits_de_groupe_test(dataset: pd.DataFrame) -> pd.DataFrame:
    return dataset[
        (dataset["split"] == "test")
        & dataset["cible"].notna()
        & dataset["taille_groupe"].notna()
    ][["credit_id", "cible"]].copy()


def mesurer_apport_couche_solidaire(
    dataset: pd.DataFrame,
    predictions_socle: pd.DataFrame,
    predictions_enrichi: pd.DataFrame,
    n_bootstrap: int = 1_000,
    graine: int = 42,
) -> ApportCoucheSolidaire:
    """`dataset` est le jeu enrichi complet (pour retrouver les crédits de groupe du test).

    `predictions_socle` et `predictions_enrichi` sont les `predictions_test` (mêmes lignes,
    mêmes `credit_id`, car les deux modèles sont entraînés sur le même jeu enrichi).
    """
    population = _population_credits_de_groupe_test(dataset)
    if population.empty:
        raise ValueError("Aucun crédit de groupe dans le test : apport non mesurable.")

    socle = population.merge(
        predictions_socle[["credit_id", "probabilite_defaut"]], on="credit_id", how="inner"
    )
    enrichi = population.merge(
        predictions_enrichi[["credit_id", "probabilite_defaut"]], on="credit_id", how="inner"
    )
    if len(socle) != len(population) or len(enrichi) != len(population):
        raise ValueError("Crédits de groupe absents des prédictions SOCLE ou enrichi.")

    cibles = population["cible"].astype(int).to_numpy()
    p_socle = socle.set_index("credit_id").loc[population["credit_id"], "probabilite_defaut"].to_numpy()
    p_enrichi = (
        enrichi.set_index("credit_id").loc[population["credit_id"], "probabilite_defaut"].to_numpy()
    )

    metriques_socle = metriques_classification(cibles, p_socle)
    metriques_enrichi = metriques_classification(cibles, p_enrichi)
    delta = {cle: metriques_enrichi[cle] - metriques_socle[cle] for cle in metriques_socle}

    generateur = np.random.RandomState(graine)
    n = len(population)
    tirages: dict[str, list[float]] = {cle: [] for cle in metriques_socle}
    for _ in range(n_bootstrap):
        indexes = generateur.randint(0, n, size=n)
        if len(np.unique(cibles[indexes])) < 2:
            continue
        m_socle = metriques_classification(cibles[indexes], p_socle[indexes])
        m_enrichi = metriques_classification(cibles[indexes], p_enrichi[indexes])
        for cle in metriques_socle:
            tirages[cle].append(m_enrichi[cle] - m_socle[cle])

    intervalles = {
        cle: (float(np.percentile(valeurs, 2.5)), float(np.percentile(valeurs, 97.5)))
        for cle, valeurs in tirages.items()
        if valeurs
    }

    return ApportCoucheSolidaire(
        n_credits=n,
        n_defauts=int(cibles.sum()),
        effectif_sous_seuil_fiabilite=n < SEUIL_FIABILITE_STATISTIQUE_R45,
        metriques_socle=metriques_socle,
        metriques_enrichi=metriques_enrichi,
        delta=delta,
        intervalle_confiance_95=intervalles,
    )
