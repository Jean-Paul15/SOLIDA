import pandas as pd

from solida_modelisation.audit import auditer_risque_fuite


def test_auc_superieure_a_088_declenche_une_revue_sans_masquer_le_resultat() -> None:
    dataset = pd.DataFrame(
        {
            "date_reference": ["2024-01-01", "2024-02-01"],
            "classe_cible": ["bon", "defaut"],
            "cible": [0, 1],
        }
    )

    audit = auditer_risque_fuite(dataset, {"auc": 0.9})

    assert audit["audit_renforce_requis"]
    assert audit["conclusion"] == "conforme"
