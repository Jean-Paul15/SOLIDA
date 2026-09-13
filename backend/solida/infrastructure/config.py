from pydantic_settings import BaseSettings


class Configuration(BaseSettings):
    """Configuration de l'API, chargée depuis l'environnement (jamais de secret en dur)."""

    solida_database_url: str
    solida_database_url_async: str
    # Vide par defaut : seul le job de purge du journal d'audit en a besoin, pas l'API — un
    # defaut requis ici forcerait tout deploiement a la fournir meme sans jamais l'utiliser.
    solida_purge_database_url: str = ""
    coresim_database_url: str
    secret_auth: str
    environnement: str = "developpement"
    seaweedfs_endpoint: str = "seaweedfs:8333"
    seaweedfs_access_key: str = ""
    seaweedfs_secret_key: str = ""
    seaweedfs_bucket: str = "solida-fiches"
    modele_socle_path: str = "/app/modeles/bundle_socle"
    modele_socle_cache_path: str = "/var/cache/solida-modele"
    mlflow_tracking_uri: str = ""
    mlflow_model_name: str = "solida-socle"
    mlflow_model_alias: str = "champion-demo"
