# MinIO et stockage objet

## Rôle

Trois usages, un seul service :

| Usage | Compartiment | Contenu |
|---|---|---|
| Fiches de justification | `fiches` | PDF archivés, immuables |
| Artefacts de modèles | `mlflow` | Modèles sérialisés, graphiques d'évaluation |
| Remote DVC | `dvc-cache` | Instantanés de données et modèles versionnés (voir `07-MLOPS/05`) |
| Instantanés de données | `snapshots` | Jeux d'entraînement, référencés par DVC |

Un seul MinIO, quatre usages. L'API S3 est unique et le remote DVC est le même service que le store
MLflow et l'archive des fiches. Aucune infrastructure de stockage supplémentaire.

## Pourquoi MinIO

Compatible S3 : le code écrit contre l'API S3 fonctionne à l'identique avec MinIO auto-hébergé
aujourd'hui et avec un stockage objet quelconque demain. Aucune réécriture.

Auto-hébergé : les fiches contiennent des données nominatives de sociétaires. Elles ne sortent pas
du périmètre de la coopérative.

## Conventions de nommage

```
fiches/{annee}/{mois}/{fiche_id}.pdf
mlflow/{experience_id}/{execution_id}/artefacts/...
snapshots/{date}/{graine}/dataset.parquet
```

Le partitionnement par année et mois est un choix d'exploitation : il permet d'appliquer une
politique de conservation par période et d'archiver ou purger simplement.

## Règles

| Règle | Motif |
|---|---|
| Les objets ne sont **jamais écrasés** | Une fiche remise est un document opposable |
| Versionnage activé sur `fiches` | Filet de sécurité supplémentaire |
| Accès via URL signée à durée limitée (15 min) | Aucun compartiment public |
| Aucun accès direct depuis le front | Le front demande une URL signée à l'API |
| Chiffrement au repos activé | Données nominatives |

Le point sur l'absence d'accès direct est important : si le front pouvait parler à MinIO, le
contrôle d'accès par rôle serait contourné.

## Politique de conservation

| Compartiment | Conservation |
|---|---|
| `fiches` | Illimitée. Document opposable |
| `mlflow` | 12 mois pour les exécutions non promues, illimitée pour les modèles ayant servi en production |
| `snapshots` | 6 mois, sauf ceux liés à un modèle en production |

Un modèle ayant servi à rendre une décision doit rester disponible aussi longtemps que la décision
peut être contestée. C'est la condition matérielle du droit à la contestation énoncé dans
`03-MODELE/06`.

## Dégradation

MinIO indisponible : le PDF est renvoyé directement dans la réponse HTTP, sans archivage, avec un
avertissement journalisé. L'agent n'est jamais bloqué par une panne de stockage.

## Périmètre hackathon

P1 : archivage des fiches. P2 : versionnage, chiffrement, politique de conservation.
Le stockage local de secours est acceptable pendant les 72 heures si MinIO pose problème, à
condition que le code passe par l'abstraction de stockage et non par le système de fichiers en dur.
