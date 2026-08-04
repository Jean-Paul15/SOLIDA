.PHONY: front-install front-dev front-lint front-typecheck front-test front-build front-down

front-install:
	docker compose run --rm front npm install

front-dev:
	docker compose up front

front-down:
	docker compose down

front-lint:
	docker compose run --rm front npm run lint

front-typecheck:
	docker compose run --rm front npm run typecheck

front-test:
	docker compose run --rm front npm run test

front-build:
	docker compose run --rm front npm run build
