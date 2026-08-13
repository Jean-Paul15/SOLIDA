# Scaffold backend et outillage Python

## Arborescence

`backend/solida/{domain,application,adapters,infrastructure,batch}/` conforme à
`01-ARCHITECTURE/02-clean-architecture.md`. Chaque sous-dossier est un module (`__init__.py` vide) ;
le contenu métier arrive module par module (domaine, ports, adaptateur `ModeleConstant`, persistance,
auth, routeurs HTTP).

Seul code réel à ce stade : `adapters/http/routeurs/health.py` (`GET /api/v1/health`, même contrat
que le mock frontend) et `infrastructure/application_fastapi.py` qui l'assemble — un contrôle de
santé complet de bout en bout plutôt que des modules vides prétendant faire quelque chose.

## Outillage (uv, ruff, mypy, pytest, import-linter)

Versions épinglées dans `backend/pyproject.toml`, vérifiées sur le registre PyPI le jour de
l'implémentation : fastapi 0.141.1, pydantic 2.13.4, pydantic-settings 2.14.2, sqlalchemy 2.0.51,
alembic 1.18.5, psycopg[binary] 3.3.4, fastapi-users[sqlalchemy] 15.0.5, argon2-cffi 25.1.0,
uvicorn[standard] 0.52.1 ; en dev : ruff 0.16.1, mypy 2.3.0, pytest 9.1.1, pytest-cov 7.1.0,
import-linter 2.13, **httpx2 2.9.1** (pas `httpx` : Starlette 1.3.1, tiré par FastAPI 0.141.1,
préfère `httpx2` pour son `TestClient` et émet un `StarletteDeprecationWarning` sinon — vérifié en
exécutant réellement la suite de tests, pas supposé).

`mypy` en `strict` (flags explicites : `disallow_any_generics`, `disallow_untyped_defs`, etc. — pas
le raccourci `strict = true`, qui n'est pas un réglage valide par module) sur `domain/` et
`application/`, plus permissif ailleurs, conformément à `04-BACKEND/02-conventions-python.md`.

`import-linter` fait respecter deux règles :
1. Couches en couches (`layers`) : `infrastructure` → `adapters` → `application` → `domain`, chacune
   ne pouvant importer que les couches strictement plus internes.
2. `domain/` ne peut importer aucune bibliothèque tierce hors Pydantic (contrat `forbidden` sur
   fastapi, sqlalchemy, alembic, psycopg, fastapi_users, uvicorn, httpx).

## Docker

`backend/Dockerfile` suit le modèle officiel `uv` (image `ghcr.io/astral-sh/uv:python3.12-trixie-slim`,
`uv sync --locked` en deux temps pour le cache de couches, utilisateur non-root `solida`). `uv.lock`
est versionné. Vérification systématique par `docker build` à froid (jamais par `exec` sur un
conteneur déjà démarré, leçon retenue du frontend) : ruff, mypy, pytest, import-linter tous verts
dans l'image reconstruite de zéro.

Ce Dockerfile n'est pas encore branché dans `docker-compose.yml` (service `api` avec ses dépendances
aux deux bases et son healthcheck : voir la suite du plan, section C).
