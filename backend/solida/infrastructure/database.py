from functools import lru_cache

from sqlalchemy import Engine, create_engine

from solida.infrastructure.config import Configuration


@lru_cache
def moteur_coresim() -> Engine:
    configuration = Configuration()
    return create_engine(configuration.coresim_database_url, pool_pre_ping=True)


@lru_cache
def moteur_solida() -> Engine:
    configuration = Configuration()
    return create_engine(configuration.solida_database_url, pool_pre_ping=True)


@lru_cache
def moteur_purge_audit() -> Engine:
    """Connexion dediee au role `solida_purge` : seul role, avec `solida_app`, ayant DELETE
    sur `journal_audit` (le trigger d'immuabilite bloque tout le reste, `solida_app` compris)."""
    configuration = Configuration()
    if not configuration.solida_purge_database_url:
        raise RuntimeError(
            "SOLIDA_PURGE_DATABASE_URL n'est pas configuree : la purge du journal d'audit "
            "ne peut pas se connecter avec le role dedie."
        )
    return create_engine(configuration.solida_purge_database_url, pool_pre_ping=True)
