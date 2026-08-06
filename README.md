# SOLIDA

Scoring d'octroi de microcrédit fondé sur la trajectoire d'épargne et le comportement de
remboursement des sociétaires de coopératives financières, avec enrichissement conditionnel sur
le segment caution solidaire.

Hackathon National d'Innovation CIF / DigiCoop-WA+, Thématique 02, Lomé, 11-13 septembre 2026.

## Architecture

- `backend/` : API FastAPI (Clean Architecture), scoring, auth, registre des décisions.
- `frontend/` : Application Next.js.
- `simulateur/` : Générateur CORE-SIM (données synthétiques d'une coopérative financière), lu en
  lecture seule par le backend, jamais écrit.
- `infra/` : Configuration nginx et scripts d'initialisation PostgreSQL.
- `docs/` : Documentation as-built (`docs/backend/`, `docs/frontend/`).

Le modèle de scoring réel (entraînement, calibration) est hors périmètre de cette passe : le
backend fonctionne avec un modèle de substitution (`ModeleConstant`), remplaçable sans changer le
reste de la chaîne, voir `docs/backend/03-decisions-provisoires-a-revoir.md`.

## Démarrage

Prérequis : Docker Desktop installé et démarré. Rien d'autre.

```bash
./scripts/demarrer.sh      # Linux / macOS / Git Bash / WSL
```
```powershell
.\scripts\demarrer.ps1     # Windows (PowerShell)
```

Le script vérifie Docker, génère `.env` et `frontend/.env` (mots de passe et secrets aléatoires,
propres à la machine) s'ils n'existent pas encore, construit les images, démarre la pile, attend
que l'API et l'interface répondent réellement (pas juste que les conteneurs soient lancés), puis
affiche l'URL à ouvrir. À la première exécution, il joue aussi les migrations, génère les données
CORE-SIM et crée les comptes de démonstration — les exécutions suivantes ne touchent plus aux
données, seulement au démarrage. Un `.env` déjà présent n'est jamais régénéré ni écrasé ; pour
repartir de zéro, le supprimer avant de relancer le script.

Seul nginx (port 80) est exposé sur l'hôte : l'application est accessible sur `http://localhost`.

### Démarrage manuel (détail de ce que fait le script, ou pour aller pas à pas)

```bash
cp .env.example .env
# completer .env (mots de passe, SECRET_AUTH, identifiants SeaweedFS...)
cp frontend/.env.example frontend/.env

docker compose up -d --build
docker compose run --rm api alembic upgrade head
```

Peupler CORE-SIM avec des données synthétiques (à refaire à chaque fois qu'on veut régénérer un
jeu de données propre) :

```bash
docker compose run --rm coresim-seed
```

Provisionner des comptes utilisateurs : c'est l'unique moyen d'en créer, aucun endpoint HTTP ne le
permet.

```bash
# comptes de démonstration (un par rôle, mot de passe partagé "solida-demo")
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes demo

# un compte réel
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes creer \
  --identifiant agent.lome --nom "Agent Lomé" --role agent --agence CAI-02

# bloquer / débloquer un compte existant
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes bloquer --identifiant agent.lome
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes debloquer --identifiant agent.lome
```

Tout compte créé via `creer` force le changement de son mot de passe à la première connexion.
Les comptes de démonstration (`demo`) en sont dispensés, ce sont des comptes de test.

## Comptes de démonstration

| Identifiant | Rôle | Agence |
|---|---|---|
| `agent.be` | agent | CAI-00 |
| `agent.agoe` | agent | CAI-01 |
| `superviseur.reseau` | superviseur | — |
| `auditeur.interne` | auditeur | — |
| `administrateur.systeme` | administrateur | — |

Mot de passe : `solida-demo` (comptes de test, changement non forcé).

## Documentation technique

- `docs/backend/` : authentification, use cases, routeurs, câblage frontend, décisions
  provisoires à recalibrer.
- `docs/frontend/` : design system, écrans, sécurité, Docker.

## Développement local

```bash
# backend
cd backend && uv sync
uv run pytest && uv run ruff check solida && uv run mypy solida && uv run lint-imports

# frontend
cd frontend && npm install
npm run typecheck && npm run lint && npm run test
```
