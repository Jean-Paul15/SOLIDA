import pandas as pd

from solida_modelisation.splits import attribuer_split, plis_temporels_entrainement


def test_decoupage_temporel_et_plis_croissants() -> None:
    dates = pd.date_range("2012-01-01", "2022-12-01", freq="YS")
    dataset = pd.DataFrame({"date_reference": dates, "cible": [0, 1] * 5 + [0]})
    dataset["split"] = attribuer_split(dataset["date_reference"])
    plis = plis_temporels_entrainement(dataset)
    assert len(plis) == 5
    for train, validation in plis:
        assert dataset.iloc[train]["date_reference"].max() < dataset.iloc[validation]["date_reference"].min()
