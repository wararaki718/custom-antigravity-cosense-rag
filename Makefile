.PHONY: build up down restart logs batch ps clean help lint test

# Default target
help:
	@echo "Available commands:"
	@echo "  make build   - Build all docker images"
	@echo "  make up      - Start all services in background"
	@echo "  make down    - Stop and remove all containers"
	@echo "  make restart - Restart all services"
	@echo "  make logs    - Show logs for all services"
	@echo "  make batch   - Run the batch ingestion service"
	@echo "  make ps      - List running services"
	@echo "  make lint    - Run linters for all components"
	@echo "  make test    - Run tests for all components"
	@echo "  make clean   - Remove all containers and volumes (Warning: deletes database data)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

batch:
	docker compose run --rm batch

ps:
	docker compose ps

lint:
	@echo "Linting encoder..."
	cd encoder && uv run ruff check .
	@echo "Linting batch..."
	cd batch && uv run ruff check .
	@echo "Linting search-api..."
	cd search-api && uv run ruff check .
	@echo "Linting ui..."
	cd ui && npm run lint

test:
	@echo "Testing encoder..."
	cd encoder && uv run pytest
	@echo "Testing batch..."
	cd batch && uv run pytest
	@echo "Testing search-api..."
	cd search-api && uv run pytest

clean:
	docker compose down -v
