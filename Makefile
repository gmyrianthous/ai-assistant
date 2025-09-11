.PHONY: down fmt fmt-check image lint logs logs-api logs-db migration-create migration-run test test-integration test-unit up

# Down the services
down:
	docker compose down

# Format the code
fmt:
	uv run ruff check --fix
	uv run ruff format

# Check the formatting
fmt-check:
	uv run ruff check

# Build the docker image
image:
	docker build -t ai-assistant .

# Lint the code
lint:
	uv run ruff check
	uv run mypy ai_assistant tests

# Follow logs continuously
logs:
	docker compose logs -f

# Follow API logs only
logs-api:
	docker compose logs -f api

# Follow DB logs only
logs-db:
	docker compose logs -f db

# Create a new migration
migration-create:
	docker compose run --rm api alembic revision -m "${revision_name}" --autogenerate

# Downgrade migration
migration-downgrade:
	docker compose run --rm api alembic downgrade -1

# Run migrations
migration-run:
	docker compose run --rm api alembic upgrade head

# Run all tests
test: test-integration test-unit

# Run integration tests only
test-integration:
	uv run pytest tests/integration -vv

# Run unit tests only
test-unit:
	uv run pytest tests/unit -vv

# Up the services
up: 
	docker compose up -d
