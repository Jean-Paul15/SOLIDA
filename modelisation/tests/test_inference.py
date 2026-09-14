import pytest

from solida_modelisation.artifact import ManifesteModele
from solida_modelisation.calibration import CalibrateurPlatt
from solida_modelisation.catalogue import codes_features_enrichi, codes_features_socle
from solida_modelisation.inference import ModeleSocle


def _manifeste(identifiant: str, features: list[str]) -> ManifesteModele:
    return ManifesteModele(
        identifiant=identifiant,
        version="test",
        commit_git="test",
        date_fin_donnees="2026-08-01",
        features=features,
        metriques_test={},
        calibrateur_platt_actif=False,
        strategie_ponderation="non_pondere",
        checksum_modele="",
        empreintes_fichiers={},
        versions_dependances={},
    )


def test_dataframe_refuse_une_feature_inconnue_du_catalogue_socle() -> None:
    modele = ModeleSocle(
        modele=object(),
        calibrateur=CalibrateurPlatt(),
        manifeste=_manifeste("solida-socle", codes_features_socle()),
    )

    with pytest.raises(ValueError, match="solida-socle.*inconnues"):
        modele._dataframe({"taille_groupe": 5})


def test_dataframe_accepte_une_feature_de_groupe_pour_le_catalogue_enrichi() -> None:
    modele = ModeleSocle(
        modele=object(),
        calibrateur=CalibrateurPlatt(),
        manifeste=_manifeste("solida-enrichi", codes_features_enrichi()),
    )

    frame = modele._dataframe({"taille_groupe": 5})

    assert "taille_groupe" in frame.columns
