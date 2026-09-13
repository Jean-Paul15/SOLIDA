# Transmission du module de modélisation

## Reprendre sur une autre machine

1. Cloner le dépôt et créer un `.env` local à partir de `.env.example`.
2. Démarrer SeaweedFS et, si nécessaire, le profil MLOps : `docker compose --profile mlops up -d seaweedfs postgres-mlflow mlops-init mlflow`.
3. Configurer le remote DVC local, sans versionner l'endpoint ni les identifiants :

   ```powershell
   dvc remote modify --local seaweedfs endpointurl http://ADRESSE_LAN:8333
   dvc remote modify --local seaweedfs access_key_id VOTRE_CLE
   dvc remote modify --local seaweedfs secret_access_key VOTRE_SECRET
   dvc pull
   ```

4. Installer l'environnement : `cd modelisation; uv sync --extra dev --extra notebooks --extra mlops`.
5. Vérifier : `uv run pytest`, puis `uv run solida-modele entrainer ...` si un nouvel entraînement est requis.

## Artefacts attendus

- `simulateur/sorties/` : sorties synthétiques brutes ;
- `modelisation/data/processed/jeu_socle.parquet` : dataset SOCLE temporel ;
- `modelisation/data/modeles/bundle_socle/` : EBM, calibrateur, manifeste et catalogue ;
- MLflow : expériences `solida-reference` et `solida-socle`. Une version y est un candidat ;
  l'alias `champion-demo` est posé manuellement après revue humaine des métriques et de
  l'audit de fuite.

Les artefacts sont contrôlés par SHA-256 au chargement. L'API privilégie MLflow, puis son cache validé, puis le bundle DVC ; elle échoue explicitement si aucune version vérifiée n'est disponible.
