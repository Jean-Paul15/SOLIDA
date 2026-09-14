.PHONY: front-install front-dev front-lint front-typecheck front-test front-build front-down \
	front-societaire-install front-societaire-dev front-societaire-lint front-societaire-typecheck \
	front-societaire-test front-societaire-build \
	back-install back-lint back-typecheck back-test back-imports

front-install:
	docker compose --profile dev run --rm front-dev npm install

front-dev:
	docker compose --profile dev up front-dev

front-down:
	docker compose --profile dev down

front-lint:
	docker compose --profile dev run --rm front-dev npm run lint

front-typecheck:
	docker compose --profile dev run --rm front-dev npm run typecheck

front-test:
	docker compose --profile dev run --rm front-dev npm run test

front-build:
	docker compose --profile dev run --rm front-dev npm run build

front-societaire-install:
	docker compose --profile dev run --rm front-societaire-dev npm install

front-societaire-dev:
	docker compose --profile dev up front-societaire-dev

front-societaire-lint:
	docker compose --profile dev run --rm front-societaire-dev npm run lint

front-societaire-typecheck:
	docker compose --profile dev run --rm front-societaire-dev npm run typecheck

front-societaire-test:
	docker compose --profile dev run --rm front-societaire-dev npm run test

front-societaire-build:
	docker compose --profile dev run --rm front-societaire-dev npm run build

back-install:
	docker compose --profile dev run --rm api-dev uv sync --locked

back-lint:
	docker compose --profile dev run --rm api-dev sh -c "uv run ruff check . && uv run ruff format --check ."

back-typecheck:
	docker compose --profile dev run --rm api-dev uv run mypy solida

back-test:
	docker compose --profile dev run --rm api-dev uv run pytest

back-imports:
	docker compose --profile dev run --rm api-dev uv run lint-imports
