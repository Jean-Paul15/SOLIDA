import pandas as pd

from solida_modelisation.catalogue import COLONNES_INTERDITES, codes_features_socle
from solida_modelisation.features import TablesBrutes, construire_jeu_socle


def _tables() -> TablesBrutes:
    societaires = pd.DataFrame(
        {
            "societaire_id": ["SOC-1"],
            "date_adhesion": ["2024-01-01"],
            "sexe": ["femme"],
            "segment": ["individuel"],
            "age": [34],
            "zone": ["rural"],
            "nb_personnes_a_charge": [2],
            "parts_sociales": [15_000],
            "revenu_declare": [100_000.0],
        }
    )
    credits = pd.DataFrame(
        {
            "credit_id": ["CRD-1", "CRD-2"],
            "societaire_id": ["SOC-1", "SOC-1"],
            "produit_id": ["prod-1", "prod-1"],
            "date_deblocage": ["2024-05-15", "2025-02-15"],
            "date_issue": ["2024-08-15", "2025-05-15"],
            "duree_mois": [3, 3],
            "montant_octroye": [50_000, 80_000],
            "defaut": [0, 1],
        }
    )
    echeances = pd.DataFrame(
        {
            "credit_id": ["CRD-1", "CRD-1", "CRD-2", "CRD-2"],
            "date_paiement_reelle": ["2024-06-15", "2024-08-15", "2025-03-15", "2025-05-15"],
            "jours_retard": [0, 0, 31, 31],
        }
    )
    soldes = pd.DataFrame(
        {
            "societaire_id": ["SOC-1"] * 15,
            "mois": pd.date_range("2024-01-01", periods=15, freq="MS"),
            "solde_fin_mois": list(range(0, 150_000, 10_000)),
            "total_depots": [10_000] * 15,
            "total_retraits": [0] * 15,
            "nb_operations": [1] * 15,
        }
    )
    produits = pd.DataFrame({"produit_id": ["prod-1"], "taux_annuel": [0.14]})
    return TablesBrutes(societaires, credits, echeances, soldes, produits)


def test_features_excluent_les_colonnes_interdites() -> None:
    dataset = construire_jeu_socle(_tables(), pd.Timestamp("2026-08-01"))
    assert set(codes_features_socle()).issubset(dataset.columns)
    assert not set(dataset.columns).intersection(COLONNES_INTERDITES)
    premier = dataset.set_index("credit_id").loc["CRD-1"]
    assert premier["nb_credits_anterieurs"] == 0
    assert pd.isna(premier["max_jours_retard_historique"])


def test_mouvements_futurs_n_affectent_pas_feature_historique() -> None:
    tables = _tables()
    original = construire_jeu_socle(tables, pd.Timestamp("2026-08-01")).set_index("credit_id")
    soldes_modifies = tables.soldes_mensuels.copy()
    soldes_modifies.loc[soldes_modifies["mois"] >= pd.Timestamp("2025-03-01"), "solde_fin_mois"] = 9_999_999
    modifie = construire_jeu_socle(
        TablesBrutes(tables.societaires, tables.credits, tables.echeances, soldes_modifies, tables.produits),
        pd.Timestamp("2026-08-01"),
    ).set_index("credit_id")
    for colonne in codes_features_socle():
        valeur_originale = original.loc["CRD-1", colonne]
        valeur_modifiee = modifie.loc["CRD-1", colonne]
        assert (pd.isna(valeur_originale) and pd.isna(valeur_modifiee)) or (
            valeur_originale == valeur_modifiee
        )
