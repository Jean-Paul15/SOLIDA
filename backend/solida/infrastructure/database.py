from functools import lru_cache

from sqlalchemy import Engine, create_engine

from solida.infrastructure.config import Configuration


@lru_cache
def coresim_engine() -> Engine:
    config = Configuration()
    return create_engine(config.coresim_database_url, pool_pre_ping=True)


@lru_cache
def solida_engine() -> Engine:
    config = Configuration()
    return create_engine(config.solida_database_url, pool_pre_ping=True)


@lru_cache
def purge_audit_engine() -> Engine:
    """Connexion dediee au role `solida_purge` : seul role, avec `solida_app`, ayant DELETE
    sur `journal_audit` (le trigger d'immuabilite bloque tout le reste, `solida_app` compris)."""
    config = Configuration()
    if not config.solida_purge_database_url:
        raise RuntimeError(
            "SOLIDA_PURGE_DATABASE_URL n'est pas configuree : la purge du journal d'audit "
            "ne peut pas se connecter avec le role dedie."
        )
    return create_engine(config.solida_purge_database_url, pool_pre_ping=True)
