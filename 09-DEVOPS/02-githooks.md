# Hooks Git

## Philosophie

Un hook empêche mécaniquement une erreur. Il ne remplace pas la discipline, il la rend inutile pour
les fautes automatisables.

**Contrainte :** un hook `pre-commit` de plus de 10 secondes sera contourné avec `--no-verify`.
Le rapide passe au commit, le lent passe au push, le très lent passe en CI.

## Outil

`pre-commit` (Python), configuré par `.pre-commit-config.yaml`, versionné.
Côté front, `husky` + `lint-staged` pour agir uniquement sur les fichiers modifiés.

## pre-commit — rapide, sur les fichiers modifiés

| Contrôle | Outil | Blocant |
|---|---|---|
| Formatage Python | `ruff format` | corrige automatiquement |
| Lint Python | `ruff check --fix` | oui si non corrigeable |
| Formatage front | `prettier` | corrige |
| Lint front | `eslint` | oui |
| Détection de secrets | `gitleaks` | **oui, toujours** |
| Fichiers volumineux | `check-added-large-files` (500 Ko) | oui |
| Fins de ligne, espaces | hooks standards | corrige |
| Validation YAML / JSON | hooks standards | oui |
| Fichiers interdits | `.env`, `*.pkl`, `*.parquet`, `*.csv` | oui |
| Conflits de fusion résiduels | `check-merge-conflict` | oui |

## commit-msg

| Contrôle | Outil |
|---|---|
| Conventional Commits | `commitizen` ou expression régulière |

## pre-push — plus lent, accepté

| Contrôle | Outil | Blocant |
|---|---|---|
| Typage | `mypy` sur `domain/` et `application/` | oui |
| Tests du domaine | `pytest tests/domain/` | oui |
| Frontières de couches | `import-linter` | oui |
| Typage front | `tsc --noEmit` | oui |

Les tests du domaine s'exécutent en moins d'une seconde : aucune raison de ne pas les passer au
push. Ce sont ceux qui portent la logique métier, donc ceux dont la régression coûte le plus cher.

## Hook spécifique : invariant de la scorecard

Un test rapide vérifie sur des cas figés que la somme des points égale le score. Il est inclus dans
les tests du domaine et donc exécuté à chaque push.

C'est l'invariant le plus important du système : s'il casse, toutes les fiches de justification
deviennent fausses sans que rien ne le signale à l'écran.

## Ce qui reste en CI uniquement

Tests d'intégration avec conteneurs, construction des images, analyse de dépendances, couverture,
tests de bout en bout.

## Installation

L'installation des hooks fait partie de la mise en route et figure dans le README de chaque dépôt.
Un développeur sans hooks est un développeur qui commitera un secret.

## Contournement

`--no-verify` est autorisé dans un seul cas : réparer d'urgence une situation bloquante, avec un
commit de correction immédiat derrière. Toute autre utilisation est un motif de discussion en
équipe.
