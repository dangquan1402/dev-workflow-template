.PHONY: help up down restart logs logs-backend shell \
       migrate migrate-create migrate-down migrate-history \
       test test-cov lint format install seed db-shell db-reset

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Docker ---

up: ## Start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail all logs
	docker compose logs -f

logs-backend: ## Tail backend logs only
	docker compose logs -f backend

shell: ## Open bash in backend container
	docker compose exec backend bash

# --- Database ---

migrate: ## Run pending migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create msg="add users table")
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback last migration
	docker compose exec backend alembic downgrade -1

migrate-history: ## Show migration history
	docker compose exec backend alembic history

db-shell: ## Open psql in postgres container
	docker compose exec postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-app_db}

db-reset: ## Drop and recreate database (DESTRUCTIVE!)
	@echo "This will destroy all data. Press Ctrl+C to cancel."
	@sleep 3
	docker compose exec postgres dropdb -U $${POSTGRES_USER:-postgres} $${POSTGRES_DB:-app_db} --if-exists
	docker compose exec postgres createdb -U $${POSTGRES_USER:-postgres} $${POSTGRES_DB:-app_db}
	docker compose exec backend alembic upgrade head

# --- Testing ---

test: ## Run all tests
	docker compose exec backend python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	docker compose exec backend python -m pytest tests/ -v --cov=app --cov-report=term-missing

# --- Code quality ---

lint: ## Run ruff check + format check
	ruff check app/ && ruff format --check app/

format: ## Auto-format with ruff
	ruff check --fix app/ && ruff format app/

# --- Setup ---

install: ## Install Python dependencies locally
	pip install -r requirements.txt
