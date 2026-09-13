# Modélisation SOCLE SOLIDA

Ce module produit une recommandation explicable de risque de défaut à partir des données synthétiques du simulateur. Il ne décide pas seul de l'octroi : les seuils d'acceptation, de revue et de refus restent des paramètres métier, décidés après revue des résultats et calibration.

## Flux reproductible

```text
simulateur/sorties -> cible et features temporelles -> référence logistique
                    -> EBM SOCLE -> calibration Platt -> bundle vérifié
```

Le SOCLE ne comporte ni sexe, ni situation matrimoniale, ni segment, ni GIE, ni garantie, ni produit, ni taux ou périodicité réellement appliqués. Ces derniers servent uniquement à reconstruire la charge estimée de la nouvelle demande avant le score. Le modèle enrichi sera une étape distincte, après validation métier des variables solidaires et sectorielles.

## Commandes locales

```powershell
uv sync --extra dev --extra notebooks --extra mlops
uv run solida-modele construire-features --source ../simulateur/sorties --sortie data/processed/jeu_socle.parquet --date-fin 2026-08-01
uv run solida-modele entrainer --dataset data/processed/jeu_socle.parquet --sortie data/modeles --modele tous
uv run pytest
uv run ruff check src tests
uv run mypy
```

`dvc repro` exécute le même flux. Les Parquet et bundles sont des sorties DVC et ne sont jamais versionnés directement par Git. Une autre machine clone le dépôt, configure localement le remote SeaweedFS (endpoint et identifiants hors Git), puis exécute `dvc pull`.

## Conteneurs

```powershell
docker build -f modelisation/Dockerfile -t solida-modelisation .
docker run --rm -v "${PWD}/simulateur/sorties:/app/sorties:ro" solida-modelisation construire-features --source /app/sorties --sortie /tmp/jeu_socle.parquet --date-fin 2026-08-01
```

Le profil Compose `mlops` démarre PostgreSQL réservé à MLflow, MLflow et l'initialisation des buckets `dvc-cache` et `mlflow` dans SeaweedFS. Les secrets restent dans `.env`, jamais dans ce dossier.

## Garanties de temporalité

`date_deblocage` est le proxy documenté de la date de demande. Toute feature ne consulte que les événements antérieurs à cette date : mois d'épargne clos, remboursements déjà enregistrés et crédits précédents. La cible est construite séparément depuis les échéances : bon 0–14 jours, indéterminé 15–29 jours, défaut dès 30 jours ; une échéance n'est évaluée qu'à maturité `date_issue + 90 jours`.

Voir [la model card](docs/model-card-socle.md), les [décisions](docs/decisions-socle.md) et la [transmission](docs/transmission-modele.md).
