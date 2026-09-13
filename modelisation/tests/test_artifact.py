import json
from pathlib import Path

import joblib
import pytest

from solida_modelisation.artifact import ManifesteModele, charger_bundle, empreinte_fichier
from solida_modelisation.calibration import CalibrateurPlatt
from solida_modelisation.catalogue import codes_features_socle


def test_bundle_altere_est_rejete(tmp_path: Path) -> None:
    modele = tmp_path / "modele.joblib"
    calibrateur = tmp_path / "calibrateur.joblib"
    catalogue = tmp_path / "catalogue_features.json"
    export = tmp_path / "modele_ebm.json"
    manquantes = tmp_path / "contributions_valeurs_manquantes.json"
    distributions = tmp_path / "distributions_reference.json"
    joblib.dump({"modele": "test"}, modele)
    joblib.dump(CalibrateurPlatt(), calibrateur)
    catalogue.write_text("[]", encoding="utf-8")
    export.write_text("{}", encoding="utf-8")
    manquantes.write_text("{}", encoding="utf-8")
    distributions.write_text("{}", encoding="utf-8")
    fichiers = [modele, calibrateur, catalogue, export, manquantes, distributions]
    manifeste = ManifesteModele(
        identifiant="solida-socle",
        version="test",
        commit_git="test",
        date_fin_donnees="2026-08-01",
        features=codes_features_socle(),
        metriques_test={},
        calibrateur_platt_actif=False,
        strategie_ponderation="non_pondere",
        checksum_modele=empreinte_fichier(modele),
        empreintes_fichiers={fichier.name: empreinte_fichier(fichier) for fichier in fichiers},
        versions_dependances={},
    )
    (tmp_path / "manifeste.json").write_text(
        json.dumps(manifeste.__dict__), encoding="utf-8"
    )
    calibrateur.write_bytes(b"artefact modifie")

    with pytest.raises(ValueError, match="calibrateur.joblib"):
        charger_bundle(tmp_path)
