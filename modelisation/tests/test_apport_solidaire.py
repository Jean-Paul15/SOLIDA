import numpy as np
import pandas as pd
import pytest

from solida_modelisation.apport_solidaire import (
    SEUIL_FIABILITE_STATISTIQUE_R45,
    mesurer_apport_couche_solidaire,
)


def _dataset(n_groupe: int, n_individuel: int) -> pd.DataFrame:
    lignes = []
    for i in range(n_groupe):
        lignes.append(
            {
                "credit_id": f"GRP-{i}",
                "split": "test",
                "cible": i % 3 == 0,
                "taille_groupe": 6,
            }
        )
    for i in range(n_individuel):
        lignes.append(
            {
                "credit_id": f"IND-{i}",
                "split": "test",
                "cible": i % 4 == 0,
                "taille_groupe": np.nan,
            }
        )
    dataset = pd.DataFrame(lignes)
    dataset["cible"] = dataset["cible"].astype(int)
    return dataset


def _predictions(dataset: pd.DataFrame, probabilite_par_ligne: dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "credit_id": dataset["credit_id"],
            "probabilite_defaut": [probabilite_par_ligne[c] for c in dataset["credit_id"]],
        }
    )


def test_apport_ignore_les_credits_individuels() -> None:
    dataset = _dataset(n_groupe=20, n_individuel=50)
    # SOCLE : prédiction constante, sans pouvoir discriminant.
    socle = _predictions(dataset, {c: 0.1 for c in dataset["credit_id"]})
    # Enrichi : prédiction parfaitement alignée sur la cible, mais seulement utile
    # sur les crédits de groupe — sur les individuels elle serait identique au SOCLE
    # en pratique (aucune variable de groupe à exploiter), ici volontairement différente
    # pour vérifier qu'elle est bien exclue de la mesure.
    enrichi = _predictions(
        dataset, {c: (0.9 if cible else 0.05) for c, cible in zip(dataset["credit_id"], dataset["cible"])}
    )

    resultat = mesurer_apport_couche_solidaire(dataset, socle, enrichi, n_bootstrap=50)

    assert resultat.n_credits == 20
    assert resultat.effectif_sous_seuil_fiabilite
    assert resultat.delta["auc"] > 0


def test_apport_signale_effectif_suffisant() -> None:
    dataset = _dataset(n_groupe=SEUIL_FIABILITE_STATISTIQUE_R45, n_individuel=0)
    socle = _predictions(dataset, {c: 0.1 for c in dataset["credit_id"]})
    enrichi = _predictions(dataset, {c: 0.1 for c in dataset["credit_id"]})

    resultat = mesurer_apport_couche_solidaire(dataset, socle, enrichi, n_bootstrap=10)

    assert not resultat.effectif_sous_seuil_fiabilite


def test_apport_leve_une_erreur_sans_credit_de_groupe() -> None:
    dataset = _dataset(n_groupe=0, n_individuel=10)
    predictions = _predictions(dataset, {c: 0.1 for c in dataset["credit_id"]})

    with pytest.raises(ValueError, match="Aucun crédit de groupe"):
        mesurer_apport_couche_solidaire(dataset, predictions, predictions, n_bootstrap=10)
