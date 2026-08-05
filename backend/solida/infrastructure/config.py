from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    """Configuration de l'API, chargée depuis l'environnement (jamais de secret en dur)."""

    solida_database_url: str
    solida_database_url_async: str
    coresim_database_url: str
    secret_auth: str
    environnement: str = "developpement"
    seaweedfs_endpoint: str = "seaweedfs:8333"
    seaweedfs_access_key: str = ""
    seaweedfs_secret_key: str = ""
    seaweedfs_bucket: str = "solida-fiches"
