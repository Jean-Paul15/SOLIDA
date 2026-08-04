# Workflow Git

## Dépôt

**Décision ADR-018 (`00-CONTEXTE/04-journal-de-decisions.md`), remplace la stratégie ci-dessous.**

Un dépôt unique `SOLIDA` (`github.com/Jean-Paul15/SOLIDA`), organisé par dossier plutôt que par
dépôt :

| Dossier | Contenu |
|---|---|
| `00-CONTEXTE/` … `10-PLAN-HACKATHON/` | Dossier de principes (`SOLIDA-FOUNDATION`), versionné |
| `frontend/` | Next.js |
| `backend/` | API, domaine, ML, batch (à venir) |
| `infra/` | Migrations, configuration additionnelle (à venir — le `docker-compose.yml` racine couvre le socle actuel) |
| `simulateur/` | Générateur CORE-SIM (à venir) |

Le cloisonnement par dossier remplace le cloisonnement par dépôt : les règles de branches
ci-dessous (branche courte, une branche par module) continuent de s'appliquer intégralement à
l'intérieur de ce dépôt unique.

<details>
<summary>Ancienne stratégie (4 dépôts séparés) — remplacée, conservée pour mémoire</summary>

Décision initiale : `solida-backend`, `solida-frontend`, `solida-simulateur`, `solida-infra`
séparés, pour que quatre personnes travaillent sans conflit permanent. Écartée par ADR-018 : avec
une équipe réduite, la coordination inter-dépôts coûtait plus qu'elle ne protégeait.
</details>

## Diffusion du dossier de principes

**Décision ADR-018 : `SOLIDA-FOUNDATION/` est versionné dans le dépôt de code, sans exclusion
`.gitignore`.** Il se propage par `git pull` comme le reste du dépôt ; toute modification passe par
une pull request comme n'importe quel autre changement, ce qui remplace le besoin d'annonce
manuelle de l'ancienne stratégie.

<details>
<summary>Ancienne décision (dossier non versionné) — remplacée, conservée pour mémoire</summary>

Décision initiale : `SOLIDA-FOUNDATION/` n'était pas versionné dans les dépôts de code, diffusé par
un canal séparé (dépôt privé, espace partagé, copie manuelle), avec annonce d'équipe à chaque mise à
jour. Écartée par ADR-018 : le risque de deux versions divergentes des règles dépassait le bénéfice
de ne pas exposer les instructions dans le code livré.
</details>

## Branches

```
main          toujours déployable
  └── feat/xxx    fonctionnalité
  └── fix/xxx     correction
  └── chore/xxx   outillage
```

Pas de `develop`. Sur trois jours, une branche d'intégration supplémentaire n'apporte que des
conflits.

**Règles :** branche courte (moins d'une journée), une branche par module pour éviter les
collisions, rebase sur `main` avant fusion, `main` jamais cassé.

## Commits — Conventional Commits

```
<type>(<portee>): <description a l'imperatif>
```

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction |
| `refactor` | Sans changement de comportement |
| `test` | Tests |
| `docs` | Documentation |
| `chore` | Outillage, dépendances |
| `perf` | Performance |

```
feat(scoring): appliquer la grille de decision au score calcule
fix(solidaire): exclure le societaire evalue du taux de remboursement du groupe
test(scorecard): verifier l invariant somme des points egale score
```

Description en français sans accents dans le sujet (compatibilité des outils), à l'impératif,
72 caractères maximum. Le corps explique le **pourquoi**, pas le comment.

**Un commit = un changement cohérent.** Ne jamais mélanger reformatage et changement fonctionnel :
le diff devient illisible et la revue impossible.

## Pull requests

Obligatoires vers `main`, même seul. C'est la trace du travail et le déclencheur de la CI.

Gabarit : ce qui change, pourquoi, comment tester, impact sur les contrats d'interface.

**La dernière ligne est la plus importante.** Un changement de contrat concerne toute l'équipe.

## Revue pendant le hackathon

Le temps manque pour des revues formelles. Compromis :

- Toute PR touchant un **contrat**, le **domaine** ou la **sécurité** : revue obligatoire.
- Le reste : fusion autorisée si la CI passe, revue a posteriori.

Cette règle est délibérée : elle protège ce qui casse tout le monde et laisse passer le reste.

## Interdits

| Interdit | Motif |
|---|---|
| Pousser directement sur `main` | Contourne la CI |
| `--force` sur une branche partagée | Détruit le travail des autres |
| Commiter un `.env` | Voir `08-SECURITE/04` |
| Commiter des données ou un modèle | Le dépôt gonfle irrémédiablement |
| Commiter du code commenté | L'historique existe pour ça |
| Un commit « wip » sur `main` | — |
