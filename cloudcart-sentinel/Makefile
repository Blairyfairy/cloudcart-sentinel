.PHONY: up down logs build migrate seed format lint typecheck test test-integration

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f api

build:
	docker compose build

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m app.seed

format:
	ruff format .
	ruff check --fix .

lint:
	ruff check .

typecheck:
	mypy app

test:
	pytest -q

test-integration:
	docker compose run --rm api pytest -q -m integration
