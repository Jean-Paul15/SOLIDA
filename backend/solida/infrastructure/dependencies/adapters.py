"""Fabriques des adaptateurs concrets, partagées entre les modules `dependencies/*.py` qui
composent les cas d'usage. Seul ce module (avec `infrastructure/auth.py`) a le droit de
connaître à la fois les ports du domaine et leurs implémentations concrètes.
"""

from functools import lru_cache
from pathlib import Path

from minio import Minio

from solida.adapters.core_sim.core_sim_postgres_reader import CoreSimPostgresReader
from solida.adapters.core_sim.feature_store_core_sim import FeatureStoreCoreSim
from solida.adapters.ml.scoring_model_ebm import EBMScoringModel
from solida.adapters.pdf.fiche_pdf_generator_weasyprint import WeasyPrintFichePdfGenerator
from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.adapters.persistence.decision_repository_sql import SqlDecisionRepository
from solida.adapters.persistence.fiche_archivee_repository_sql import SqlFicheArchiveeRepository
from solida.adapters.persistence.grille_repository_sql import SqlGrilleRepository
from solida.adapters.storage.fiche_repository_seaweedfs import SeaweedfsFicheRepository
from solida.infrastructure.config import Configuration
from solida.infrastructure.database import coresim_engine, solida_engine


@lru_cache
def core_sim_reader() -> CoreSimPostgresReader:
    return CoreSimPostgresReader(coresim_engine())


@lru_cache
def feature_store() -> FeatureStoreCoreSim:
    return FeatureStoreCoreSim(core_sim_reader())


@lru_cache
def scoring_model() -> EBMScoringModel:
    configuration = Configuration()
    return EBMScoringModel(
        fallback_path=Path(configuration.modele_socle_path),
        cache_path=Path(configuration.modele_socle_cache_path),
        tracking_uri=configuration.mlflow_tracking_uri,
        model_name=configuration.mlflow_model_name,
        model_alias=configuration.mlflow_model_alias,
    )


@lru_cache
def decision_repository() -> SqlDecisionRepository:
    return SqlDecisionRepository(solida_engine())


@lru_cache
def grille_repository() -> SqlGrilleRepository:
    return SqlGrilleRepository(solida_engine())


@lru_cache
def audit_log() -> SqlAuditLog:
    return SqlAuditLog(solida_engine())


@lru_cache
def _client_seaweedfs() -> Minio:
    configuration = Configuration()
    return Minio(
        configuration.seaweedfs_endpoint,
        access_key=configuration.seaweedfs_access_key,
        secret_key=configuration.seaweedfs_secret_key,
        secure=False,
    )


@lru_cache
def fiche_repository() -> SeaweedfsFicheRepository:
    configuration = Configuration()
    return SeaweedfsFicheRepository(_client_seaweedfs(), configuration.seaweedfs_bucket)


@lru_cache
def fiche_archivee_repository() -> SqlFicheArchiveeRepository:
    return SqlFicheArchiveeRepository(solida_engine())


@lru_cache
def fiche_pdf_generator() -> WeasyPrintFichePdfGenerator:
    return WeasyPrintFichePdfGenerator()
