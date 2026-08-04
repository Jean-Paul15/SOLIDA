# DVC — versionnage des données et des modèles

## Rôle et complémentarité avec MLflow

DVC et MLflow ne font pas la même chose et se complètent.

| Outil | Responsabilité |
|---|---|
| **DVC** | Versionner les **données** et les **artefacts de modèle** en lien avec Git, garantir le lignage et la reproductibilité |
| **MLflow** | Suivre les **expériences** (paramètres, métriques), comparer, tenir le registre des modèles |

DVC répond à « quelles données et quel modèle exactement ont produit ce résultat », MLflow répond à
« quelle expérience a donné quelles métriques ». On utilise les deux.

## Licence et pérennité

DVC est open source sous licence Apache 2.0, écrit en Python. Le projet a changé de tutelle fin 2025
(racheté par lakeFS) mais reste 100 % open source sous la même licence, et reste orienté vers les
jeux de données de taille modérée, ce qui est exactement notre cas. On n'a pas besoin de lakeFS, qui
vise l'échelle du data lake.

**À surveiller (sans conséquence immédiate) :** un changement de tutelle est un bon moment pour
garder un œil sur la feuille de route. Notre usage est basique et facilement remplaçable si besoin.

## Pourquoi DVC ici et pas autre chose

| Option | Décision |
|---|---|
| **DVC** | **Retenu.** Léger, aucun serveur, s'appuie sur Git, remote S3 (donc MinIO) |
| lakeFS | Écarté : conçu pour des data lakes à l'échelle du pétaoctet, surdimensionné |
| Git LFS | Écarté : versionne des binaires mais ne gère ni pipeline ni lignage de données |
| Rien | Écarté : sans versionnage de données, aucune décision n'est rejouable à l'identique |

## Ce qui est versionné avec DVC

| Élément | Suivi |
|---|---|
| Instantané des données d'entraînement | `.dvc` pointant vers MinIO |
| Modèles sérialisés (socle, enrichi, référence) | `.dvc` |
| Calibrateurs | `.dvc` |
| Catalogue de features figé par version | Git (petit fichier) |
| Configuration du générateur (YAML) | Git |

**Ce qui n'est jamais versionné dans Git directement :** les données et les modèles eux-mêmes. Git
ne suit que les fichiers `.dvc` (des pointeurs légers), les vraies données vivent dans MinIO.

## Remote : MinIO, mutualisé

Le remote DVC est le **même MinIO** que celui de MLflow et des fiches. Un seul stockage objet, trois
usages :

```
minio/
├── dvc-cache/          instantanés de données et modèles versionnés (remote DVC)
├── mlflow/             artefacts d'expériences MLflow
└── fiches/             fiches de justification PDF
```

Aucune infrastructure supplémentaire. L'API S3 est unique.

## Pipeline reproductible

DVC permet de décrire le pipeline dans `dvc.yaml` : génération → features → entraînement →
évaluation. Chaque étape déclare ses entrées et ses sorties. `dvc repro` rejoue exactement ce qui a
changé, avec cache.

Pour le hackathon, ce n'est pas obligatoire dès le jour 1, mais le lien graine du générateur →
instantané versionné → modèle versionné doit exister **avant le premier modèle promu**, sinon la
reproductibilité annoncée dans le pitch n'est pas vraie.

## Reproductibilité complète, avec MLflow

| Question | Répondu par |
|---|---|
| Quelles données ? | DVC (instantané) + graine du générateur |
| Quel code ? | Git (empreinte de commit) |
| Quel environnement ? | `uv.lock` |
| Quels hyperparamètres et métriques ? | MLflow |
| Quel modèle exactement ? | DVC (artefact) + registre MLflow |

Un entraînement est reproductible au chiffre près des mois plus tard. C'est la condition matérielle
de l'audit d'une décision.

## Périmètre hackathon

**P1.** À mettre en place tôt, car le coût est faible et le bénéfice (reproductibilité démontrable)
est un argument fort devant le jury. Montrer que n'importe quel score peut être rejoué avec
exactement les mêmes données et le même modèle est rare dans un hackathon et très convaincant.
