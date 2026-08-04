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
