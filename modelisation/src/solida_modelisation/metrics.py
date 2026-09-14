"""Métriques de discrimination, calibration et recommandation."""

from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
)


def erreur_calibration_attendue(y_true: np.ndarray, probabilites: np.ndarray, bins: int = 10) -> float:
    """ECE pondérée en classes de probabilité de même largeur."""
    indices = np.minimum((probabilites * bins).astype(int), bins - 1)
    total = len(y_true)
    if total == 0:
        return 0.0
    erreur = 0.0
    for indice in range(bins):
        masque = indices == indice
        if not masque.any():
            continue
        erreur += masque.mean() * abs(float(y_true[masque].mean()) - float(probabilites[masque].mean()))
    return float(erreur)


def ecart_maximal_deciles(y_true: np.ndarray, probabilites: np.ndarray, bins: int = 10) -> float:
    """Écart observé/prédit dans des déciles de population, pas de largeur fixe."""
    try:
        indices = pd.qcut(probabilites, q=bins, labels=False, duplicates="drop")
        # Sur un vecteur de probabilités constant (ou presque), `qcut` ne lève pas
        # `ValueError` : il renvoie des labels entièrement `NaN`, faute de pouvoir former
        # des bornes de bin distinctes. Un seul décile couvre alors toute la population.
        if pd.isna(indices).all():
            indices = np.zeros(len(probabilites), dtype=int)
    except ValueError:
        indices = np.zeros(len(probabilites), dtype=int)
    ecarts: list[float] = []
    for indice in range(int(np.max(indices)) + 1):
        masque = indices == indice
        if masque.any():
            ecarts.append(abs(float(y_true[masque].mean()) - float(probabilites[masque].mean())))
    return max(ecarts, default=0.0)


def metriques_classification(y_true: Iterable[int], probabilites: Iterable[float]) -> dict[str, float]:
    y = np.asarray(list(y_true), dtype=int)
    p = np.clip(np.asarray(list(probabilites), dtype=float), 1e-8, 1 - 1e-8)
    return {
        "auc": float(roc_auc_score(y, p)),
        "gini": float(2 * roc_auc_score(y, p) - 1),
        "auprc": float(average_precision_score(y, p)),
        "log_loss": float(log_loss(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "ece": erreur_calibration_attendue(y, p),
        "ecart_max_decile": ecart_maximal_deciles(y, p),
    }


def courbe_precision_rappel(
    y_true: Iterable[int], probabilites: Iterable[float]
) -> pd.DataFrame:
    """Expose les compromis possibles sans décréter de seuil de décision."""
    y = np.asarray(list(y_true), dtype=int)
    p = np.clip(np.asarray(list(probabilites), dtype=float), 1e-8, 1 - 1e-8)
    precision, rappel, seuils = precision_recall_curve(y, p)
    return pd.DataFrame(
        {
            "seuil_probabilite": seuils,
            "precision_defaut": precision[:-1],
            "rappel_defaut": rappel[:-1],
        }
    )
