"""Construction déterministe de la cible de défaut à 30 jours."""

import numpy as np
import pandas as pd


def construire_cible(
    credits: pd.DataFrame, echeances: pd.DataFrame, date_fin: pd.Timestamp
) -> pd.DataFrame:
    """Retourne les quatre classes, sans lire les issues synthétiques du crédit."""
    credits_local = credits.copy()
    credits_local["date_issue"] = pd.to_datetime(credits_local["date_issue"])
    maximums = echeances.groupby("credit_id", as_index=False).agg(
        retard_max_cible=("jours_retard", "max")
    )
    resultat = credits_local[["credit_id", "date_issue"]].merge(maximums, on="credit_id", how="left")
    mature = resultat["date_issue"] + pd.Timedelta(days=90) <= pd.Timestamp(date_fin)
    retard = resultat["retard_max_cible"]
    resultat["classe_cible"] = np.select(
        [~mature, retard >= 30, retard < 15],
        ["en_cours", "defaut", "bon"],
        default="indetermine",
    )
    resultat["cible"] = pd.Series(pd.NA, index=resultat.index, dtype="Int64")
    resultat.loc[resultat["classe_cible"] == "bon", "cible"] = 0
    resultat.loc[resultat["classe_cible"] == "defaut", "cible"] = 1
    return resultat[["credit_id", "classe_cible", "cible", "retard_max_cible"]]
