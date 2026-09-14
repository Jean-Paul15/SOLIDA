"""Adaptateur du bundle EBM SOCLE vers le port métier de scoring."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from mlflow import artifacts
from mlflow.tracking import MlflowClient
from solida_modelisation.inference import ModeleSocle

from solida.domain.values.features import ValeurFeature
from solida.domain.values.probabilite import ProbabiliteDefaut

logger = logging.getLogger(__name__)


class EBMScoringModel:
    """Charge le champion MLflow, puis un cache vérifié, puis le bundle DVC local."""

    def __init__(
        self,
        fallback_path: Path,
        cache_path: Path,
        tracking_uri: str = "",
        model_name: str = "solida-socle",
        model_alias: str = "champion-demo",
        nom_artefact_bundle: str = "bundle_socle",
    ) -> None:
        self._source = "fallback_dvc"
        self._modele = self._charger(
            tracking_uri=tracking_uri,
            model_name=model_name,
            model_alias=model_alias,
            cache_path=cache_path,
            fallback_path=fallback_path,
            nom_artefact_bundle=nom_artefact_bundle,
        )

    def _charger(
        self,
        tracking_uri: str,
        model_name: str,
        model_alias: str,
        cache_path: Path,
        fallback_path: Path,
        nom_artefact_bundle: str,
    ) -> ModeleSocle:
        if tracking_uri:
            try:
                client = MlflowClient(tracking_uri=tracking_uri)
                client.get_model_version_by_alias(model_name, model_alias)
                uri = f"models:/{model_name}@{model_alias}"
                racine_modele = Path(
                    artifacts.download_artifacts(artifact_uri=uri, tracking_uri=tracking_uri)
                )
                telecharge = racine_modele / "artifacts" / nom_artefact_bundle
                if not telecharge.is_dir():
                    telecharge = racine_modele / nom_artefact_bundle
                if not telecharge.is_dir():
                    raise ValueError(
                        f"Le modèle MLflow ne contient pas le bundle "
                        f"{nom_artefact_bundle!r} attendu."
                    )
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                temporaire = cache_path.with_name(f"{cache_path.name}.nouveau")
                if temporaire.exists():
                    shutil.rmtree(temporaire)
                shutil.copytree(telecharge, temporaire)
                ModeleSocle.depuis_dossier(temporaire)
                if cache_path.exists():
                    shutil.rmtree(cache_path)
                temporaire.replace(cache_path)
                self._source = "registre_mlflow"
                return ModeleSocle.depuis_dossier(cache_path)
            except Exception as erreur:
                # Un registre indisponible ne doit pas empêcher le repli vers un artefact vérifié.
                logger.warning(
                    "Chargement MLflow indisponible, repli vers artefact vérifié : %s",
                    erreur,
                )
        if cache_path.exists():
            try:
                self._source = "cache_verifie"
                return ModeleSocle.depuis_dossier(cache_path)
            except (OSError, TypeError, ValueError) as erreur:
                logger.warning("Cache SOCLE invalide, essai du bundle DVC : %s", erreur)
        self._source = "fallback_dvc"
        return ModeleSocle.depuis_dossier(fallback_path)

    def identifiant(self) -> str:
        return self._modele.identifiant

    def version(self) -> str:
        return f"{self._modele.version}+{self._modele.checksum[:12]}"

    def variables_attendues(self) -> list[str]:
        return self._modele.codes

    def predire(self, features: dict[str, ValeurFeature]) -> ProbabiliteDefaut:
        return ProbabiliteDefaut(self._modele.predire(features))

    def contributions(self, features: dict[str, ValeurFeature]) -> list[tuple[str, float]]:
        return self._modele.contributions_log_odds_bon(features)
