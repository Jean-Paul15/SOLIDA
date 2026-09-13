"""Bundle versionné et vérifié du modèle SOCLE."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .calibration import CalibrateurPlatt
from .catalogue import FEATURES_SOCLE, codes_features_socle


@dataclass(frozen=True)
class ManifesteModele:
    identifiant: str
    version: str
    commit_git: str
    date_fin_donnees: str
    features: list[str]
    metriques_test: dict[str, float]
    calibrateur_platt_actif: bool
    strategie_ponderation: str
    checksum_modele: str
    empreintes_fichiers: dict[str, str]
    versions_dependances: dict[str, str]


def empreinte_fichier(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for bloc in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(bloc)
    return digest.hexdigest()


def _distributions_reference(features: pd.DataFrame) -> dict[str, dict[str, object]]:
    resultat: dict[str, dict[str, object]] = {}
    for specification in FEATURES_SOCLE:
        serie = features[specification.code]
        manquants = float(serie.isna().mean())
        if specification.type_ebm == "continue":
            numerique = pd.to_numeric(serie, errors="coerce").dropna()
            resultat[specification.code] = {
                "type": "continue",
                "part_manquante": manquants,
                "p05": float(numerique.quantile(0.05)) if not numerique.empty else None,
                "median": float(numerique.median()) if not numerique.empty else None,
                "p95": float(numerique.quantile(0.95)) if not numerique.empty else None,
            }
        else:
            frequences = serie.astype("string").fillna("__manquant__").value_counts(normalize=True)
            resultat[specification.code] = {
                "type": specification.type_ebm,
                "part_manquante": manquants,
                "frequences": {str(cle): float(valeur) for cle, valeur in frequences.items()},
            }
    return resultat


def _versions_dependances() -> dict[str, str]:
    return {
        paquet: version(paquet)
        for paquet in ("interpret-core", "pandas", "scikit-learn", "joblib")
    }


def sauvegarder_bundle(
    dossier: Path,
    modele: Any,
    calibrateur: CalibrateurPlatt,
    commit_git: str,
    date_fin_donnees: str,
    metriques_test: dict[str, float],
    strategie_ponderation: str = "non_pondere",
    features_reference: pd.DataFrame | None = None,
    version: str = "0.1.0",
) -> ManifesteModele:
    dossier.mkdir(parents=True, exist_ok=True)
    modele_path = dossier / "modele.joblib"
    joblib.dump(modele, modele_path)
    checksum = empreinte_fichier(modele_path)
    joblib.dump(calibrateur, dossier / "calibrateur.joblib")
    (dossier / "catalogue_features.json").write_text(
        json.dumps([asdict(feature) for feature in FEATURES_SOCLE], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    export_json = getattr(modele, "to_json", None)
    if callable(export_json):
        export_json(dossier / "modele_ebm.json", detail="interpretable", indent=2)
    termes = getattr(modele, "term_features_", ())
    scores_termes = getattr(modele, "term_scores_", ())
    contributions_manquantes: dict[str, float] = {}
    for indexes, scores in zip(termes, scores_termes, strict=True):
        if len(indexes) != 1:
            continue
        index_feature = int(indexes[0])
        code = codes_features_socle()[index_feature]
        # EBM réserve l'index 0 de chaque terme à la branche missing="separate".
        contributions_manquantes[code] = calibrateur.contribution_bon(float(scores[0]))
    (dossier / "contributions_valeurs_manquantes.json").write_text(
        json.dumps(contributions_manquantes, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    distributions = _distributions_reference(
        features_reference if features_reference is not None else pd.DataFrame(columns=codes_features_socle())
    )
    (dossier / "distributions_reference.json").write_text(
        json.dumps(distributions, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    fichiers_a_verifier = [
        modele_path,
        dossier / "calibrateur.joblib",
        dossier / "catalogue_features.json",
        dossier / "modele_ebm.json",
        dossier / "contributions_valeurs_manquantes.json",
        dossier / "distributions_reference.json",
    ]
    empreintes_fichiers = {
        fichier.name: empreinte_fichier(fichier) for fichier in fichiers_a_verifier
    }
    manifeste = ManifesteModele(
        identifiant="solida-socle",
        version=version,
        commit_git=commit_git,
        date_fin_donnees=date_fin_donnees,
        features=codes_features_socle(),
        metriques_test=metriques_test,
        calibrateur_platt_actif=calibrateur.actif,
        strategie_ponderation=strategie_ponderation,
        checksum_modele=checksum,
        empreintes_fichiers=empreintes_fichiers,
        versions_dependances=_versions_dependances(),
    )
    (dossier / "manifeste.json").write_text(
        json.dumps(asdict(manifeste), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifeste


def charger_bundle(dossier: Path) -> tuple[Any, CalibrateurPlatt, ManifesteModele]:
    contenu = json.loads((dossier / "manifeste.json").read_text(encoding="utf-8"))
    manifeste = ManifesteModele(**contenu)
    for nom, empreinte_attendue in manifeste.empreintes_fichiers.items():
        fichier = dossier / nom
        if not fichier.is_file() or empreinte_fichier(fichier) != empreinte_attendue:
            raise ValueError(f"Empreinte du fichier SOCLE invalide : {nom}.")
    modele_path = dossier / "modele.joblib"
    if empreinte_fichier(modele_path) != manifeste.checksum_modele:
        raise ValueError("Empreinte du modèle SOCLE invalide.")
    if manifeste.features != codes_features_socle():
        raise ValueError("Catalogue des features incompatible avec le bundle SOCLE.")
    modele = joblib.load(modele_path)
    calibrateur = joblib.load(dossier / "calibrateur.joblib")
    if not isinstance(calibrateur, CalibrateurPlatt):
        raise TypeError("Calibrateur SOCLE invalide.")
    return modele, calibrateur, manifeste
