# Docker et développement

## Ce que démarre `docker compose up`

Le service `front` de `docker-compose.yml` sert désormais un **build de production** (`next build`
+ `next start` via la sortie `standalone`, cible `runner` du Dockerfile) — jamais `next dev`. C'est
ce que route `nginx` en frontal (audit F2 : un serveur de développement ne doit jamais être exposé,
même en démo, à cause des chemins internes qu'il expose et du panneau de dev accessible à tous).

## Développement local (rechargement à chaud)

```
make front-dev
```

Démarre `front-dev` (profil `dev`, jamais inclus dans un `docker compose up` par défaut, jamais
routé par nginx). Le code source est monté en volume, `node_modules` et `.next` vivent dans des
volumes nommés pour ne pas être écrasés par le montage.

## Commandes disponibles

| Commande | Effet |
|---|---|
| `make front-install` | `npm install` dans le conteneur `front-dev` |
| `make front-dev` | Démarre le serveur de développement (`next dev`, Turbopack) |
| `make front-lint` | `eslint` |
| `make front-typecheck` | `tsc --noEmit` |
| `make front-test` | `vitest run` |
| `make front-build` | `next build` (vérifie que le build de production passe) |
| `make front-down` | Arrête et retire les conteneurs (profil `dev` inclus) |

Aucune de ces commandes ne nécessite Node installé sur la machine — tout tourne dans le conteneur.

## Dockerfile

Quatre étapes dans un seul fichier (`frontend/Dockerfile`) :

1. `deps` — installe les dépendances (`npm ci`)
2. `dev` — cible du service `front-dev` (développement local uniquement), code monté en volume
3. `builder` — `next build`, sortie `standalone`
4. `runner` — cible du service `front` (celui que `docker compose up` démarre et que nginx route),
   image finale minimale, utilisateur non-root (`node`), healthcheck sur `/api/v1/health`

## Sécurité du conteneur

- Utilisateur non-root (`node`) dans l'image finale.
- `cap_drop: ALL` et `no-new-privileges` sur le service `front`.
- Aucun secret dans l'image : tout passe par `frontend/.env` (non versionné, généré depuis
  `.env.example`).
- Télémétrie Next.js désactivée (`NEXT_TELEMETRY_DISABLED=1`) — aucun appel sortant non nécessaire.
- Réseau Docker dédié (`solida`) ; seul `nginx` publie un port vers l'hôte, `front` n'est jamais
  atteignable directement (voir `infra/nginx/nginx.conf`).

## Bug connu en amont : panique Turbopack en HMR (mode dev uniquement)

Observé en vérification bout en bout : `next dev` (Turbopack) peut paniquer (`turbo-tasks: an
internal panic occurred outside the per-task panic boundary`) après plusieurs cycles de compilation
à chaud rapprochés — pas une régression du code applicatif, et sans effet sur le build de production
réellement déployé. N'affecte que `front-dev` (développement local) ; `front-dev` n'a pas de
`restart: unless-stopped` (usage interactif), relancer `make front-dev` si ça arrive.

## Ce qui n'existe pas encore dans `docker-compose.yml`

`mlflow` reste à construire par le module qui le nécessite. `api`, `postgres-coresim`,
`postgres-solida`, `nginx` et `seaweedfs` (stockage objet des fiches archivées, remplace le MinIO
initialement prévu, voir `docs/backend/03-decisions-provisoires-a-revoir.md`) existent déjà.
