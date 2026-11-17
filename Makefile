.PHONY: dev api web test lint ingest qdrant-up qdrant-down qdrant-logs

dev: ## run API + UI (two terminals recommended: make api / make web)
	@echo "Use: make api  (terminal 1) and  make web  (terminal 2)"

api:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd web && npm run dev

test:
	uv run pytest -q

lint:
	uv run ruff check app config ingest tests

ingest:
	uv run python -m ingest --source all

qdrant-up:
	docker compose up -d qdrant

qdrant-down:
	docker compose down

qdrant-logs:
	docker compose logs -f qdrant
