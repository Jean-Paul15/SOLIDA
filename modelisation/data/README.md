# Données versionnées par DVC

Les Parquet et bundles ne sont jamais committés. Après avoir configuré localement l'endpoint
SeaweedFS et les identifiants S3, exécuter `dvc pull` depuis la racine du dépôt.

Les sorties attendues sont `processed/jeu_socle.parquet` et `modeles/bundle_socle/`.
