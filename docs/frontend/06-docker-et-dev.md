# Docker et développement

## Une commande pour démarrer

```
make front-dev
```

Équivalent à `docker compose up front`. Le code source est monté en volume (rechargement à chaud),
`node_modules` et `.next` vivent dans des volumes nommés pour ne pas être écrasés par le montage.

## Commandes disponibles

| Commande | Effet |
|---|---|
| `make front-install` | `npm install` dans le conteneur |
| `make front-dev` | Démarre le serveur de développement |
| `make front-lint` | `eslint` |
| `make front-typecheck` | `tsc --noEmit` |
| `make front-test` | `vitest run` |
| `make front-build` | `next build` |
| `make front-down` | Arrête et retire les conteneurs |

Aucune de ces commandes ne nécessite Node installé sur la machine — tout tourne dans le conteneur.

## Dockerfile

Quatre étapes dans un seul fichier (`frontend/Dockerfile`) :

1. `deps` — installe les dépendances (`npm ci`)
2. `dev` — cible utilisée par `docker-compose.yml`, code monté en volume
3. `builder` — `next build`, sortie `standalone`
4. `runner` — image finale minimale, utilisateur non-root (`node`), healthcheck sur `/api/v1/sante`

## Sécurité du conteneur

- Utilisateur non-root (`node`) dans l'image finale.
- `cap_drop: ALL` et `no-new-privileges` sur le service `front`.
- Aucun secret dans l'image : tout passe par `frontend/.env` (non versionné, généré depuis
  `.env.example`).
- Télémétrie Next.js désactivée (`NEXT_TELEMETRY_DISABLED=1`) — aucun appel sortant non nécessaire.
- Réseau Docker dédié (`solida`) ; seul `nginx` publie un port vers l'hôte, `front` n'est plus
  atteignable directement (voir `infra/nginx/nginx.conf`).

## Bug connu en amont : `next build` échoue sur `/_global-error`

`npm run build` (donc la cible `builder`/`runner` du Dockerfile) échoue actuellement avec
`TypeError: Cannot read properties of null (reading 'useContext')` pendant le prerendering de la
page d'erreur globale interne `/_global-error`. Confirmé comme régression connue de Next.js 16
(16.0.1 à 16.3.0, la dernière stable au moment d'écrire ceci), sans correctif ni contournement
disponible côté application — voir
[vercel/next.js#86178](https://github.com/vercel/next.js/issues/86178) et
[discussion #94667](https://github.com/vercel/next.js/discussions/94667). N'affecte pas le mode
développement (`next dev`, utilisé par `docker-compose.yml` et donc par la démo) ni
`typecheck`/`lint`/`test`. Bloque uniquement un déploiement en image `runner` figée. À réessayer à
chaque mise à jour de Next.js 16.

## Bug connu en amont : panique Turbopack en HMR

Observé en vérification bout en bout : `next dev` (Turbopack, mode conteneur) peut paniquer
(`turbo-tasks: an internal panic occurred outside the per-task panic boundary`) après plusieurs
cycles de compilation à chaud rapprochés — pas une régression du code applicatif. `front` a donc
`restart: unless-stopped` dans `docker-compose.yml` pour se relever seul sans intervention. À
réessayer à chaque mise à jour de Next.js 16.

## Ce qui n'existe pas encore dans `docker-compose.yml`

`mlflow` reste à construire par le module qui le nécessite. `api`, `postgres-coresim`,
`postgres-solida`, `nginx` et `seaweedfs` (stockage objet des fiches archivées, remplace le MinIO
initialement prévu — voir `docs/backend/03-decisions-provisoires-a-revoir.md`) existent déjà.
