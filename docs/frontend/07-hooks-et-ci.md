# Hooks Git et CI

## Activation (une fois par clone)

```
git config core.hooksPath frontend/.husky
```

Déjà fait sur ce dépôt. Un nouveau clone doit lancer cette commande une fois — c'est une commande
Git, pas une commande applicative, elle ne passe donc pas par Docker.

## Hooks

| Hook | Contrôle | Où ça tourne |
|---|---|---|
| `pre-commit` | `lint-staged` (`eslint --fix` + `prettier --write` sur les fichiers modifiés) | Conteneur `node:22` jetable, dépôt entier monté (nécessaire pour que `git` voie les fichiers indexés) |
| `commit-msg` | Format Conventional Commits, sujet sans accents | Shell pur, pas de conteneur |
| `pre-push` | `tsc --noEmit` | Conteneur `node:22` jetable |

`node:22` (pas la variante `slim`) est utilisé pour les hooks parce qu'il embarque `git`, requis par
`lint-staged` pour lire les fichiers indexés — le Dockerfile applicatif (image de production), lui,
reste sur `node:22-slim`. Un volume nommé `solida_frontend_node_modules` évite de réinstaller les
dépendances à chaque commit.

## Ce qui manque volontairement

Le hook `pre-commit` de `09-DEVOPS/02-githooks.md` prévoit aussi `gitleaks` et
`check-added-large-files` — ils sont couverts par `.pre-commit-config.yaml` (framework Python
`pre-commit`), pas par Husky, parce qu'ils sont indépendants du langage et s'appliqueront aussi au
futur backend.

## CI

`.github/workflows/frontend-ci.yml` : lint, typage, tests, build — déclenché sur les push et PR
touchant `frontend/**`.
