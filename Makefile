.PHONY: down fmt fmt-check image lint test test-integration test-unit up

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
