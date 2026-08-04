# Intégration continue

## Périmètre hackathon

Une CI est utile mais ne doit pas consommer le temps du hackathon. Décision :

| Élément | Avant le hackathon | Pendant |
|---|---|---|
| Lint et typage | Oui | Oui |
| Tests du domaine | Oui | Oui |
| Tests d'intégration | Oui | Si le temps le permet |
| Construction d'images | Oui | Non |
| Déploiement automatique | Non | Non |

**Mettre la CI en place avant le hackathon** est du temps parfaitement investi : elle tourne
ensuite toute seule et empêche l'accumulation de dette pendant les 72 heures.

## Étapes du pipeline

```
1. Installation      uv sync / npm ci, avec cache
2. Lint              ruff / eslint
3. Typage            mypy / tsc
4. Frontières        import-linter
5. Tests domaine     rapides, sans dépendance
6. Tests application avec doublures
7. Tests intégration testcontainers
8. Couverture        100 % exigé sur domain/rules/
9. Secrets           gitleaks sur la branche
10. Construction     images Docker
```

Les étapes 2 à 5 s'exécutent en moins d'une minute. Elles doivent tourner sur **chaque** push.
Les étapes 7 à 10 peuvent être réservées aux PR vers `main`.

## Conditions de fusion

| Condition | Blocant |
|---|---|
| Lint sans erreur | oui |
| Typage sans erreur | oui |
| Tous les tests passent | oui |
| Couverture de `domain/rules/` à 100 % | oui |
| Aucun secret détecté | oui |
| Aucune frontière de couche violée | oui |
| Revue si contrat / domaine / sécurité | oui |

## Environnement de démonstration

Objectif : reconstruire l'environnement complet en une commande, avec des données figées et
vérifiées.

```
make demo
```

Ce que fait cette commande : démarrer les services, appliquer les migrations, générer CORE-SIM avec
la graine de démonstration, lancer le batch, charger le modèle promu, vérifier la sonde de santé.

**Elle doit être testée plusieurs fois avant le départ pour Lomé.** Le pire scénario du hackathon
est une démonstration qui ne démarre pas devant le jury parce que personne n'a rejoué la procédure
depuis la veille.

## Après le hackathon

Déploiement continu sur un environnement de recette, déploiement manuel en production avec
approbation, migrations en étape distincte et bloquante, retour arrière par étiquette d'image.
