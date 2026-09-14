"""Entraînement des références logistique et EBM SOCLE."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from interpret.glassbox import ExplainableBoostingClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from .artifact import ManifesteModele, sauvegarder_bundle
from .calibration import CalibrateurPlatt
from .catalogue import (
    FEATURES_ENRICHI,
    FEATURES_SOCLE,
    FeatureSpec,
    codes_features_socle,
    types_ebm,
)
from .equite import ecarts_a_risque_comparable, rapport_par_strate, seuil_revue_humaine
from .metrics import courbe_precision_rappel, metriques_classification
from .splits import plis_temporels_entrainement


@dataclass(frozen=True)
class ResultatEntrainement:
    modele: Any
    calibrateur: CalibrateurPlatt
    metriques_validation: dict[str, float]
    metriques_test: dict[str, float]
    resultats_recherche: pd.DataFrame
    predictions_test: pd.DataFrame
    comparaison_ponderation: pd.DataFrame | None = None
    manifeste: ManifesteModele | None = None


def _jeu_par_split(dataset: pd.DataFrame, split: str) -> pd.DataFrame:
    resultat = dataset[(dataset["split"] == split) & dataset["cible"].notna()].copy()
    resultat["cible"] = resultat["cible"].astype(int)
    if resultat.empty:
        raise ValueError(f"Aucune ligne entraînable dans le split {split}.")
    return resultat.sort_values("date_reference").reset_index(drop=True)


def _preparer_ebm(frame: pd.DataFrame, catalogue: tuple[FeatureSpec, ...]) -> pd.DataFrame:
    codes = [feature.code for feature in catalogue]
    resultat = frame[codes].copy()
    for feature in catalogue:
        if feature.type_ebm == "continue":
            resultat[feature.code] = pd.to_numeric(resultat[feature.code], errors="coerce")
        else:
            resultat[feature.code] = resultat[feature.code].astype("object").where(
                resultat[feature.code].notna(), np.nan
            )
    return resultat


def _logit_defaut(probabilites: np.ndarray) -> np.ndarray:
    p = np.clip(probabilites, 1e-8, 1 - 1e-8)
    return np.asarray(np.log(p / (1 - p)), dtype=float)


def _calibrer_si_necessaire(
    probabilites_validation: np.ndarray, y_validation: np.ndarray
) -> CalibrateurPlatt:
    metriques = metriques_classification(y_validation, probabilites_validation)
    calibrateur = CalibrateurPlatt()
    if metriques["ece"] >= 0.03 or metriques["ecart_max_decile"] >= 0.05:
        calibrateur.fit(_logit_defaut(probabilites_validation), y_validation)
    return calibrateur


def _predictions_audit(test: pd.DataFrame, probabilites: np.ndarray) -> pd.DataFrame:
    audit = [
        "credit_id",
        "societaire_id",
        "date_reference",
        "cible",
        "zone_residence",
        "numero_cycle",
        "sexe_audit",
        "segment_audit",
        "tranche_montant_audit",
    ]
    presentes = [colonne for colonne in audit if colonne in test]
    return test[presentes].assign(probabilite_defaut=probabilites)


def _creer_ebm(
    params: dict[str, Any], catalogue: tuple[FeatureSpec, ...] = FEATURES_SOCLE
) -> ExplainableBoostingClassifier:
    return ExplainableBoostingClassifier(
        feature_names=[feature.code for feature in catalogue],
        feature_types=types_ebm(catalogue),
        missing="separate",
        random_state=42,
        n_jobs=1,
        **params,
    )


def _fit_ebm(
    modele: ExplainableBoostingClassifier,
    x: pd.DataFrame,
    y: pd.Series,
    poids: np.ndarray | None = None,
) -> ExplainableBoostingClassifier:
    with warnings.catch_warnings():
        # EBM conserve bien une branche missing="separate" ; l'export JSON dédié rend
        # ensuite les contributions de cette branche auditables sans polluer le journal.
        warnings.filterwarnings("ignore", message="Missing values detected.*", category=UserWarning)
        modele.fit(x, y, sample_weight=poids)
    return modele


def _comparer_ponderation(
    x: pd.DataFrame,
    y: pd.Series,
    plis: list[tuple[np.ndarray, np.ndarray]],
    params: dict[str, Any],
    baseline: pd.Series,
    catalogue: tuple[FeatureSpec, ...],
) -> pd.DataFrame:
    """Évalue le seul mécanisme natif d'équilibrage d'EBM, par plis temporels.

    Les poids sont recalculés dans chaque sous-ensemble d'entraînement ; ainsi la
    prévalence du pli de validation ne fuit jamais dans le modèle.
    """
    mesures: list[dict[str, float]] = []
    for indexes_train, indexes_validation in plis:
        x_train, x_validation = x.iloc[indexes_train], x.iloc[indexes_validation]
        y_train, y_validation = y.iloc[indexes_train], y.iloc[indexes_validation]
        poids = compute_sample_weight("balanced", y_train.to_numpy())
        modele = _fit_ebm(_creer_ebm(params, catalogue), x_train, y_train, poids)
        probabilites = modele.predict_proba(x_validation)[:, 1]
        mesures.append(metriques_classification(y_validation, probabilites))
    ponderee = pd.DataFrame(mesures)
    return pd.DataFrame(
        [
            {
                "strategie": "non_pondere",
                "log_loss_cv": -float(baseline["mean_test_neg_log_loss"]),
                "auprc_cv": float(baseline["mean_test_auprc"]),
                "auc_cv": float(baseline["mean_test_roc_auc"]),
                "ecart_type_auc_cv": float(baseline["std_test_roc_auc"]),
            },
            {
                "strategie": "sample_weight_balanced",
                "log_loss_cv": float(ponderee["log_loss"].mean()),
                "auprc_cv": float(ponderee["auprc"].mean()),
                "auc_cv": float(ponderee["auc"].mean()),
                "ecart_type_auc_cv": float(ponderee["auc"].std(ddof=0)),
            },
        ]
    )


def entrainer_reference_logistique(dataset: pd.DataFrame) -> ResultatEntrainement:
    train = _jeu_par_split(dataset, "train")
    validation = _jeu_par_split(dataset, "validation")
    test = _jeu_par_split(dataset, "test")
    categories = [spec.code for spec in FEATURES_SOCLE if spec.type_ebm != "continue"]
    numeriques = [spec.code for spec in FEATURES_SOCLE if spec.type_ebm == "continue"]
    pretraitement = ColumnTransformer(
        [
            (
                "numeriques",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                        ("normaliser", StandardScaler()),
                    ]
                ),
                numeriques,
            ),
            (
                "categories",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="constant", fill_value="__manquant__")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", min_frequency=0.01)),
                    ]
                ),
                categories,
            ),
        ]
    )
    pipeline = Pipeline(
        [("pretraitement", pretraitement), ("modele", LogisticRegression(max_iter=2_000, random_state=42))]
    )
    recherche = RandomizedSearchCV(
        pipeline,
        param_distributions={"modele__C": [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]},
        n_iter=7,
        scoring={"neg_log_loss": "neg_log_loss", "roc_auc": "roc_auc", "auprc": "average_precision"},
        refit="neg_log_loss",
        cv=plis_temporels_entrainement(train),
        random_state=42,
        n_jobs=-1,
        error_score="raise",
    )
    recherche.fit(train[codes_features_socle()], train["cible"])
    modele = recherche.best_estimator_
    p_val = modele.predict_proba(validation[codes_features_socle()])[:, 1]
    calibrateur = _calibrer_si_necessaire(p_val, validation["cible"].to_numpy())
    p_val_calibre = calibrateur.predire(_logit_defaut(p_val))
    p_test = modele.predict_proba(test[codes_features_socle()])[:, 1]
    p_test_calibre = calibrateur.predire(_logit_defaut(p_test))
    return ResultatEntrainement(
        modele=modele,
        calibrateur=calibrateur,
        metriques_validation=metriques_classification(validation["cible"], p_val_calibre),
        metriques_test=metriques_classification(test["cible"], p_test_calibre),
        resultats_recherche=pd.DataFrame(recherche.cv_results_),
        predictions_test=_predictions_audit(test, p_test_calibre),
    )


def _entrainer_ebm(
    dataset: pd.DataFrame,
    catalogue: tuple[FeatureSpec, ...],
    identifiant: str,
    dossier_bundle: Path | None = None,
    commit_git: str = "inconnu",
) -> ResultatEntrainement:
    train = _jeu_par_split(dataset, "train")
    validation = _jeu_par_split(dataset, "validation")
    test = _jeu_par_split(dataset, "test")
    x_train = _preparer_ebm(train, catalogue)
    x_validation = _preparer_ebm(validation, catalogue)
    x_test = _preparer_ebm(test, catalogue)
    estimateur = _creer_ebm({}, catalogue)
    recherche = RandomizedSearchCV(
        estimateur,
        param_distributions={
            "max_leaves": [2, 3],
            "interactions": [0, 5, 10],
            "learning_rate": [0.01, 0.015, 0.03],
            "min_samples_leaf": [4, 10, 20],
            "max_bins": [128, 256, 512],
            "outer_bags": [8, 14],
            "early_stopping_tolerance": [0.0, 1e-5],
        },
        n_iter=40,
        scoring={
            "neg_log_loss": "neg_log_loss",
            "roc_auc": "roc_auc",
            "auprc": "average_precision",
            "neg_brier": "neg_brier_score",
        },
        refit=False,
        cv=plis_temporels_entrainement(train),
        random_state=42,
        n_jobs=-1,
        error_score="raise",
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Missing values detected.*", category=UserWarning)
        recherche.fit(x_train, train["cible"])
    resultats = pd.DataFrame(recherche.cv_results_)
    stables = resultats[resultats["std_test_roc_auc"] < 0.03]
    candidats = stables if not stables.empty else resultats
    meilleur = candidats.sort_values(["mean_test_neg_log_loss", "mean_test_auprc"], ascending=False).iloc[0]
    params = meilleur["params"]
    plis = plis_temporels_entrainement(train)
    comparaison_ponderation = _comparer_ponderation(
        x_train, train["cible"], plis, params, meilleur, catalogue
    )
    candidat_pondere = comparaison_ponderation.loc[
        comparaison_ponderation["strategie"] == "sample_weight_balanced"
    ].iloc[0]
    utiliser_ponderation = bool(
        candidat_pondere["log_loss_cv"] < -float(meilleur["mean_test_neg_log_loss"])
        and candidat_pondere["ecart_type_auc_cv"] < 0.03
    )
    poids_finaux = (
        compute_sample_weight("balanced", train["cible"].to_numpy()) if utiliser_ponderation else None
    )
    strategie_ponderation = "sample_weight_balanced" if utiliser_ponderation else "non_pondere"
    modele = _fit_ebm(_creer_ebm(params, catalogue), x_train, train["cible"], poids_finaux)
    p_val = modele.predict_proba(x_validation)[:, 1]
    calibrateur = _calibrer_si_necessaire(p_val, validation["cible"].to_numpy())
    p_val_calibre = calibrateur.predire(_logit_defaut(p_val))
    p_test = modele.predict_proba(x_test)[:, 1]
    p_test_calibre = calibrateur.predire(_logit_defaut(p_test))
    manifeste = None
    if dossier_bundle is not None:
        manifeste = sauvegarder_bundle(
            dossier_bundle,
            modele,
            calibrateur,
            commit_git=commit_git,
            date_fin_donnees="2026-08-01",
            metriques_test=metriques_classification(test["cible"], p_test_calibre),
            strategie_ponderation=strategie_ponderation,
            features_reference=x_train,
            catalogue=catalogue,
            identifiant=identifiant,
        )
    return ResultatEntrainement(
        modele=modele,
        calibrateur=calibrateur,
        metriques_validation=metriques_classification(validation["cible"], p_val_calibre),
        metriques_test=metriques_classification(test["cible"], p_test_calibre),
        resultats_recherche=resultats,
        predictions_test=_predictions_audit(test, p_test_calibre),
        comparaison_ponderation=comparaison_ponderation,
        manifeste=manifeste,
    )


def entrainer_socle_ebm(
    dataset: pd.DataFrame, dossier_bundle: Path | None = None, commit_git: str = "inconnu"
) -> ResultatEntrainement:
    return _entrainer_ebm(dataset, FEATURES_SOCLE, "solida-socle", dossier_bundle, commit_git)


def entrainer_enrichi_ebm(
    dataset: pd.DataFrame, dossier_bundle: Path | None = None, commit_git: str = "inconnu"
) -> ResultatEntrainement:
    """Même procédure que le SOCLE, sur le catalogue étendu de la couche solidaire."""
    return _entrainer_ebm(dataset, FEATURES_ENRICHI, "solida-enrichi", dossier_bundle, commit_git)


def ecrire_rapport_resultat(resultat: ResultatEntrainement, dossier: Path, nom: str) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([resultat.metriques_validation]).assign(split="validation").to_json(
        dossier / f"{nom}_validation.json", orient="records", indent=2
    )
    pd.DataFrame([resultat.metriques_test]).assign(split="test").to_json(
        dossier / f"{nom}_test.json", orient="records", indent=2
    )
    resultats = resultat.resultats_recherche.copy()
    resultats.to_parquet(dossier / f"{nom}_recherche.parquet", index=False)
    if resultat.comparaison_ponderation is not None:
        resultat.comparaison_ponderation.to_json(
            dossier / f"{nom}_comparaison_ponderation.json", orient="records", indent=2
        )
    resultat.predictions_test.to_parquet(dossier / f"{nom}_predictions_test.parquet", index=False)
    courbe_precision_rappel(
        resultat.predictions_test["cible"], resultat.predictions_test["probabilite_defaut"]
    ).to_parquet(dossier / f"{nom}_courbe_precision_rappel.parquet", index=False)
    strates = rapport_par_strate(resultat.predictions_test)
    strates.to_json(dossier / f"{nom}_resultats_par_strate.json", orient="records", indent=2)
    ecarts = ecarts_a_risque_comparable(resultat.predictions_test)
    ecarts.to_json(dossier / f"{nom}_equite.json", orient="records", indent=2)
    (dossier / f"{nom}_revue_equite.json").write_text(
        pd.Series(
            {
                "seuil_selection_non_defini": True,
                "revue_humaine_ecart_risque_superieur_5_points": seuil_revue_humaine(ecarts),
            }
        ).to_json(indent=2),
        encoding="utf-8",
    )
