# Makefile at repo root
.PHONY: format lint type test check run devb up

format:
	ruff check --fix .
	ruff format .

lint:
	ruff check .

type:
	mypy .

test:
	uv run pytest -q

check:
	uv run pre-commit run --all-files

devb:
	docker compose -f docker-compose.yml up --build

up:
	docker compose -f docker-compose.yml up

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000