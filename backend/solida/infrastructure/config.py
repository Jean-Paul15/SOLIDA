from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    """Configuration de l'API, chargee depuis l'environnement (jamais de secret en dur)."""

    solida_database_url: str
    coresim_database_url: str
