.PHONY: front-install front-dev front-lint front-typecheck front-test front-build front-down

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
