.PHONY: help setup up down logs test test-api clean build restart

help: ## Show this help message
	@echo "Media Generation API - Development Commands"
	@echo "==========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy env file and create directories
	cp .env-example .env
	mkdir -p storage/media
	@echo "✅ Environment file created from .env-example"
	@echo "✅ Storage directory created"
	@echo "📝 Next steps:"
	@echo "   1. Edit .env with your Replicate API token"
	@echo "   2. Run 'make up' to start services"

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "✅ Services starting..."
	@echo "   API: http://localhost:8000"
	@echo "   Docs: http://localhost:8000/docs"
	@echo "   Flower: http://localhost:5555"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-worker: ## Show Celery worker logs
	docker-compose logs -f celery_worker

test: ## Run tests
	python -m pytest tests/ -v

test-api: ## Test API endpoints manually
	python scripts/test_api.py

dev-api: ## Start API in development mode
	python scripts/run_dev.py

dev-worker: ## Start Celery worker in development mode
	python scripts/start_worker.py

status: ## Show service status
	docker-compose ps

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

shell-api: ## Get shell in API container
	docker-compose exec api bash

shell-worker: ## Get shell in worker container
	docker-compose exec celery_worker bash

db-shell: ## Connect to PostgreSQL
	docker-compose exec postgres psql -U postgres -d media_generation

redis-cli: ## Connect to Redis CLI
	docker-compose exec redis redis-cli

migration: ## Create new database migration
	alembic revision --autogenerate -m "$(MSG)"

migrate: ## Apply database migrations
	alembic upgrade head

install: ## Install Python dependencies locally
	pip install -r requirements.txt

format: ## Format code (if you add black/ruff)
	@echo "Add black and ruff to requirements.txt for formatting"

requirements: ## Update requirements.txt
	pip freeze > requirements.txt 