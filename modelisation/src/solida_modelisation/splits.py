"""Découpages temporels figés du SOCLE."""

import numpy as np
import pandas as pd


def attribuer_split(date_reference: pd.Series) -> pd.Series:
    annees = pd.to_datetime(date_reference).dt.year
    return pd.Series(
        np.select(
            [annees <= 2022, annees == 2023, annees >= 2024],
            ["train", "validation", "test"],
            default="hors_perimetre",
        ),
        index=date_reference.index,
        dtype="string",
    )


def plis_temporels_entrainement(dataset: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    """Cinq plis expansifs, dont chaque validation est postérieure à son entraînement."""
    dates = pd.to_datetime(dataset["date_reference"])
    annees = dates.dt.year
    plis: list[tuple[np.ndarray, np.ndarray]] = []
    for annee_validation in range(2018, 2023):
        train = np.flatnonzero((annees < annee_validation).to_numpy())
        validation = np.flatnonzero((annees == annee_validation).to_numpy())
        if len(train) == 0 or len(validation) == 0:
            raise ValueError(f"Pli temporel invalide pour {annee_validation}.")
        plis.append((train, validation))
    return plis
