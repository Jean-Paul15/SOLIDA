"""Journalisation MLflow des entraînements et du bundle SOCLE."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd


def _dependances_mlflow() -> tuple[Any, Any, Any, Any]:
    """Importe MLflow uniquement quand le suivi est explicitement activé.

    Le package de construction des features et le bundle restent utilisables sans
    installer MLflow ; celui-ci appartient au profil MLOps optionnel.
    """
    try:
        import mlflow
        import mlflow.pyfunc
        import mlflow.sklearn
        from mlflow.models import infer_signature
        from mlflow.tracking import MlflowClient
    except ImportError as erreur:
        raise RuntimeError(
            "MLFLOW_TRACKING_URI est défini mais MLflow n'est pas installé. "
            "Installez l'extra 'mlops'."
        ) from erreur
    return mlflow, infer_signature, MlflowClient, mlflow.pyfunc


def actif() -> bool:
    return bool(os.environ.get("MLFLOW_TRACKING_URI"))


def _journaliser_metriques(mlflow: Any, prefixe: str, metriques: dict[str, float]) -> None:
    mlflow.log_metrics({f"{prefixe}_{cle}": valeur for cle, valeur in metriques.items()})


def journaliser_reference(
    modele: Any,
    metriques_validation: dict[str, float],
    metriques_test: dict[str, float],
    exemple: pd.DataFrame,
) -> None:
    if not actif():
        return
    mlflow, infer_signature, _, _ = _dependances_mlflow()
    mlflow.set_experiment("solida-reference")
    with mlflow.start_run(run_name="reference-logistique-temporelle"):
        _journaliser_metriques(mlflow, "validation", metriques_validation)
        _journaliser_metriques(mlflow, "test", metriques_test)
        mlflow.log_param("graine", 42)
        signature = infer_signature(exemple, modele.predict_proba(exemple))
        mlflow.sklearn.log_model(modele, name="reference_logistique", signature=signature)


def _journaliser_ebm(
    identifiant: str,
    experience: str,
    run_name: str,
    nom_artefact_bundle: str,
    metriques_validation: dict[str, float],
    metriques_test: dict[str, float],
    bundle: Path,
    exemple: pd.DataFrame,
    promouvoir_champion_demo: bool,
) -> None:
    if not actif():
        return
    mlflow, infer_signature, client_type, pyfunc = _dependances_mlflow()

    class PyfuncEbm(pyfunc.PythonModel):  # type: ignore[misc, name-defined]
        """Interface MLflow qui charge le même bundle vérifié que l'API."""

        def load_context(self, context: Any) -> None:
            from .inference import ModeleSocle

            self._modele = ModeleSocle.depuis_dossier(Path(context.artifacts[nom_artefact_bundle]))

        def predict(self, context: Any, model_input: pd.DataFrame, params: Any = None) -> pd.DataFrame:
            probabilites = [
                self._modele.predire({str(cle): valeur for cle, valeur in ligne.items()})
                for ligne in model_input.to_dict("records")
            ]
            return pd.DataFrame({"probabilite_defaut": probabilites})

    mlflow.set_experiment(experience)
    with mlflow.start_run(run_name=run_name):
        _journaliser_metriques(mlflow, "validation", metriques_validation)
        _journaliser_metriques(mlflow, "test", metriques_test)
        mlflow.log_param("graine", 42)
        signature = infer_signature(exemple, pd.DataFrame({"probabilite_defaut": [0.0] * len(exemple)}))
        info = mlflow.pyfunc.log_model(
            name=nom_artefact_bundle,
            python_model=PyfuncEbm(),
            artifacts={nom_artefact_bundle: str(bundle)},
            signature=signature,
            input_example=exemple.head(3),
            registered_model_name=identifiant,
        )
        if promouvoir_champion_demo and info.registered_model_version is not None:
            client_type().set_registered_model_alias(
                identifiant, "champion-demo", str(info.registered_model_version)
            )


def journaliser_socle(
    metriques_validation: dict[str, float],
    metriques_test: dict[str, float],
    bundle: Path,
    exemple: pd.DataFrame,
    promouvoir_champion_demo: bool = False,
) -> None:
    _journaliser_ebm(
        "solida-socle",
        "solida-socle",
        "socle-ebm-temporel",
        "bundle_socle",
        metriques_validation,
        metriques_test,
        bundle,
        exemple,
        promouvoir_champion_demo,
    )


def journaliser_enrichi(
    metriques_validation: dict[str, float],
    metriques_test: dict[str, float],
    bundle: Path,
    exemple: pd.DataFrame,
    promouvoir_champion_demo: bool = False,
) -> None:
    """Candidat seulement : aucun alias `champion-demo` n'est posé automatiquement (J2-03)."""
    _journaliser_ebm(
        "solida-enrichi",
        "solida-enrichi",
        "enrichi-ebm-temporel",
        "bundle_enrichi",
        metriques_validation,
        metriques_test,
        bundle,
        exemple,
        promouvoir_champion_demo,
    )
