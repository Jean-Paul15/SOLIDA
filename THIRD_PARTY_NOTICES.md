# Composants tiers et logiciels libres

Solution SOLIDA, équipe Sophos. Le périmètre créé par l'équipe est sous Apache
License 2.0 (fichier `LICENSE`). Ce fichier recense les composants tiers et
logiciels libres **de premier niveau** intégrés à la solution, avec leur version
épinglée et leur licence (identifiant SPDX), vérifiée à la source (registre npm,
PyPI, dépôts officiels) le 2026-09-02.

L'inventaire **complet** des dépendances (directes et transitives) est donné par :

- `docs/livrables/sbom-frontend.txt` (855 paquets) et `frontend/package-lock.json`
- `docs/livrables/sbom-backend.txt` (81 paquets) et `backend/uv.lock`
- `simulateur/requirements.txt`

Toutes les dépendances transitives relèvent des mêmes familles de licences
permissives (MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, 0BSD, Zlib,
Python-2.0). Les seuls composants sous copyleft faible (LGPL-3.0) sont les
pilotes PostgreSQL, signalés ci-dessous. Aucune dépendance applicative n'est
sous copyleft fort (GPL, AGPL).

## Frontend (exécution)

| Composant | Version | Licence (SPDX) | Usage |
|---|---|---|---|
| next | 16.3.0 | MIT | Framework React, rendu serveur et routage |
| react | 19.2.8 | MIT | Bibliothèque de composants d'interface |
| react-dom | 19.2.8 | MIT | Rendu DOM de React |
| radix-ui | 1.6.7 | MIT | Primitives d'interface accessibles |
| recharts | 3.10.1 | MIT | Graphiques (trajectoire d'épargne, simulations) |
| framer-motion | 12.43.0 | MIT | Animations d'interface |
| lucide-react | 1.28.0 | ISC | Jeu d'icônes |
| cmdk | 1.1.1 | MIT | Palette de commandes et recherche |
| sonner | 2.0.7 | MIT | Notifications transitoires |
| clsx | 2.1.1 | MIT | Concaténation conditionnelle de classes CSS |
| tailwind-merge | 3.6.0 | MIT | Fusion des classes utilitaires Tailwind |
| class-variance-authority | 0.7.1 | Apache-2.0 | Composition des variantes de style |

## Frontend (développement, construction, test ; hors chemin d'exécution)

| Composant | Version | Licence (SPDX) | Usage |
|---|---|---|---|
| tailwindcss | 4.3.3 | MIT | Feuilles de style utilitaires |
| @tailwindcss/postcss | 4.3.3 | MIT | Intégration PostCSS de Tailwind |
| tw-animate-css | 1.4.0 | MIT | Utilitaires d'animation Tailwind |
| typescript | 5.9.3 | Apache-2.0 | Typage statique |
| eslint | 9.39.5 | MIT | Analyse statique |
| eslint-config-next | 16.3.0 | MIT | Règles ESLint Next.js |
| prettier | 3.9.6 | MIT | Formatage du code |
| husky | 9.1.7 | MIT | Hooks Git |
| lint-staged | 17.3.0 | MIT | Vérifications de pré-commit |
| shadcn | 4.16.1 | MIT | CLI de génération de composants (copiés dans le dépôt sous MIT) |
| vitest | 4.1.10 | MIT | Tests unitaires |
| @types/node | 22.20.1 | MIT | Déclarations de types |
| @types/react | 19.2.18 | MIT | Déclarations de types |
| @types/react-dom | 19.2.4 | MIT | Déclarations de types |

## Backend et API (exécution)

| Composant | Version | Licence (SPDX) | Usage |
|---|---|---|---|
| fastapi | 0.141.1 | MIT | Framework de l'API de scoring |
| pydantic | 2.13.4 | MIT | Validation des schémas de données |
| pydantic-settings | 2.14.2 | MIT | Chargement de la configuration |
| sqlalchemy | 2.0.51 | MIT | Accès relationnel (ORM et Core) |
| alembic | 1.18.5 | MIT | Migrations de la base SOLIDA |
| psycopg[binary] | 3.3.4 | **LGPL-3.0-only** | Pilote PostgreSQL (voir la note sur la LGPL) |
| fastapi-users[sqlalchemy] | 15.0.5 | MIT | Authentification et gestion des comptes agents |
| argon2-cffi | 25.1.0 | MIT | Hachage des mots de passe (Argon2) |
| uvicorn[standard] | 0.52.1 | BSD-3-Clause | Serveur ASGI |
| weasyprint | 69.0 | BSD-3-Clause | Rendu PDF de la fiche de justification |
| jinja2 | 3.1.6 | BSD-3-Clause | Gabarit HTML de la fiche |
| minio | 7.2.20 | Apache-2.0 | Client S3 (stockage des fiches archivées) |

## Backend (développement, test, construction ; hors chemin d'exécution)

| Composant | Version | Licence (SPDX) | Usage |
|---|---|---|---|
| ruff | 0.16.1 | MIT | Lint |
| mypy | 2.3.0 | MIT | Vérification de types |
| pytest | 9.1.1 | MIT | Tests |
| pytest-cov | 7.1.0 | MIT | Couverture de tests |
| httpx | 0.28.1 | BSD-3-Clause | Client HTTP de test |
| import-linter | 2.13 | BSD-2-Clause | Contrôle des couches (Clean Architecture) |
| hatchling | (build) | MIT | Backend de construction du paquet |

## Simulateur, générateur de données synthétiques (exécution)

| Composant | Version | Licence (SPDX) | Usage |
|---|---|---|---|
| numpy | 2.5.1 | BSD-3-Clause (bundles 0BSD, MIT, Zlib, CC0-1.0) | Calcul numérique |
| pandas | 3.0.5 | BSD-3-Clause | Manipulation des jeux de données |
| pyyaml | 6.0.3 | MIT | Lecture de la configuration du générateur |
| sqlalchemy | 2.0.51 | MIT | Chargement vers PostgreSQL |
| psycopg2-binary | 2.9.12 | **LGPL-3.0-or-later** (avec exceptions de compilation) | Pilote PostgreSQL du chargement |
| pyarrow | 25.0.0 | Apache-2.0 | Lecture et écriture au format Parquet (moteur de pandas) |

## Infrastructure, images Docker de base

| Image | Version | Licence | Usage |
|---|---|---|---|
| node:22-slim | 22 | Node.js : MIT ; base Debian : distribution système (licences multiples) | Image d'exécution du frontend |
| python:3.12-slim | 3.12 | Python : Python-2.0 (PSF) ; base Debian : distribution système | Image d'exécution du simulateur |
| ghcr.io/astral-sh/uv | python3.12-trixie-slim | uv : MIT OR Apache-2.0 ; base Debian | Image de construction et d'exécution du backend |
| postgres | 16.14 | PostgreSQL (type BSD/MIT) ; base Debian | Bases SOLIDA et CORE-SIM |
| nginx | 1.30.4-alpine | nginx : BSD-2-Clause ; base Alpine : distribution système | Reverse proxy, point d'entrée réseau unique |
| chrislusf/seaweedfs | 4.40 | Apache-2.0 ; base : distribution système | Stockage objet compatible S3 |

Les images Docker de base sont des distributions système standard, utilisées
sans modification. Leur contenu (userland Debian ou Alpine) inclut des paquets
sous copyleft, dont GPL, comme toute distribution Linux ; ils constituent
l'environnement d'exécution et ne sont ni liés ni incorporés au code de la
Solution. Le code de la Solution et ses dépendances applicatives (Python et
JavaScript) ne contiennent aucun composant sous copyleft fort.

## Note sur la LGPL (psycopg et psycopg2-binary)

Licence : **GNU LGPL v3** (`psycopg` : `LGPL-3.0-only` ; `psycopg2-binary` :
`LGPL-3.0-or-later` avec exceptions de compilation).

Droits accordés : usage commercial et privé sans redevance ; **intégration dans
un logiciel propriétaire ou fermé sans obligation de publier le code de ce
logiciel** ; modification et redistribution de la bibliothèque.

Obligations : si les fichiers internes de la bibliothèque sont modifiés, ces
modifications doivent être publiées sous LGPL ; les mentions de copyright et de
licence d'origine doivent être conservées. Le logiciel est fourni sans garantie.

Application à SOLIDA : les deux pilotes sont utilisés **tels quels** (installés
par `pip`/`uv`, importés sans modification) et liés dynamiquement. Aucune
obligation de diffusion du code de SOLIDA n'en découle. La cession et
l'exploitation prévues par la Charte de la CIF, y compris pour une solution dont
la propriété est transférée, restent possibles : il suffit que le pilote demeure
non modifié et remplaçable (SQLAlchemy permet de changer de pilote PostgreSQL
sans toucher au code applicatif).
