.PHONY: dev api web test lint

dev: ## run API + UI (two terminals recommended: make api / make web)
	@echo "Use: make api  (terminal 1) and  make web  (terminal 2)"

api:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd web && npm run dev

test:
	uv run pytest -q

lint:
	uv run ruff check app tests
