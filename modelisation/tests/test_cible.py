import pandas as pd

from solida_modelisation.cible import construire_cible


def test_frontieres_j15_et_j30_et_maturite() -> None:
    credits = pd.DataFrame(
        {
            "credit_id": ["bon", "j15", "defaut", "encours"],
            "date_issue": ["2026-04-01", "2026-04-01", "2026-04-01", "2026-07-01"],
        }
    )
    echeances = pd.DataFrame(
        {
            "credit_id": ["bon", "j15", "defaut", "encours"],
            "jours_retard": [14, 15, 30, 0],
        }
    )
    cible = construire_cible(credits, echeances, pd.Timestamp("2026-08-01")).set_index("credit_id")
    assert cible.loc["bon", "classe_cible"] == "bon"
    assert cible.loc["bon", "cible"] == 0
    assert cible.loc["j15", "classe_cible"] == "indetermine"
    assert pd.isna(cible.loc["j15", "cible"])
    assert cible.loc["defaut", "classe_cible"] == "defaut"
    assert cible.loc["defaut", "cible"] == 1
    assert cible.loc["encours", "classe_cible"] == "en_cours"
