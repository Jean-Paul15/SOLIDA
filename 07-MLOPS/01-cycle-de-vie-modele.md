# Cycle de vie du modèle

## Les six étapes

```
1. Données      instantané versionné, découpage temporel
2. Entraînement graine fixée, paramètres journalisés
3. Évaluation   métriques sur le jeu de test, par segment
4. Calibration  vérification et correction
5. Promotion    contrôles de qualité, puis passage en production
6. Surveillance dérive, distribution des scores, taux de bascule
```

Aucune étape n'est sautée, y compris pendant le hackathon. Un modèle promu sans étape 4 produit
une scorecard dont l'échelle ne veut rien dire.

## Contrôles de promotion

Un modèle ne passe en production que si **tous** ces contrôles passent. Ils sont automatisés.

| Contrôle | Seuil |
|---|---|
| AUC sur le jeu de test | ≥ 0,70 |
| AUC non supérieure à | 0,88 — au-delà, suspecter une fuite |
| Erreur de calibration attendue | < 0,03 |
| Invariant de décomposition | vérifié sur 1 000 dossiers |
| Aucune variable sensible | vérification par liste |
| AUC par segment | aucun segment sous 0,60 |
| Stabilité sur 5 découpages | écart-type < 0,03 |
| Toutes les variables du catalogue documentées | 100 % |

Le contrôle de **plafond** d'AUC est inhabituel et volontaire. Sur des données que nous générons
nous-mêmes, une performance trop belle est le signe d'un problème, pas d'une réussite. Mieux vaut
le détecter automatiquement que devant le jury.

## Versionnage

Format : `{type}-{aaaammjj}-{n}`, par exemple `socle-20260912-3`.

Chaque version enregistre : graine des données, période d'entraînement, hyperparamètres, versions
des librairies, métriques complètes, catalogue des variables, empreinte de l'artefact.

## Promotion et retrait

| État | Signification |
|---|---|
| `entraine` | Existe, non évalué |
| `evalue` | Métriques disponibles |
| `candidat` | Contrôles passés, en attente de décision |
| `production` | Actif. **Un seul par type** |
| `retire` | Remplacé, conservé pour le rejeu |

**Un modèle retiré n'est jamais supprimé.** Des décisions ont été rendues avec lui ; elles doivent
rester rejouables.

## Retour arrière

Un retour à la version précédente doit prendre moins de cinq minutes et ne consister qu'en un
changement d'état en base plus un rechargement. Aucun redéploiement, aucune reconstruction
d'image.

## Reproductibilité

| Élément | Moyen |
|---|---|
| Données | Graine du générateur + instantané dans MinIO |
| Code | Empreinte de commit |
| Environnement | `uv.lock` |
| Aléatoire | Graine fixée et journalisée |
| Résultats | Métriques dans MLflow |

Un entraînement doit être reproductible au chiffre près six mois plus tard. Si ce n'est pas le
cas, l'audit d'une décision est impossible.
