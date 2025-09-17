# 🤖💬 AI Assistant Python Template
This is a production-ready Python template that can be used to ship agentic systems with FastAPI
and LangGraph. The template aims to provide a boilerplate solution with batteries included, 
including:
- API (FastAPI)
- AI Agents (LangGraph, Tools)
- User Interface (assistant-ui)
- Monitoring & Observability (Grafana, LangFuse)
- Model Evaluations (LangFuse)
- CI/CD (GitHub Actions)


## 🌟 Features

### ⚙️ API
The backend implementation exposes endpoints that facilitate:
- Session Management 
- Interactions between the chatbot and the end user 

> The swagger documentation for the available endpoints can be accessed on 
> https://localhost:8080/docs

### 💾 Data Store


### 💡AI


### 🖥️ User Interface


> **_Note:_**  The default model used in the boilerplate code is set to Google Gemini on Vertex AI,
> however, the code structure lets you choose the language model of your preference with minimal 
> changes required, due to the abstractions put in place.

### ♾️ CI/CD
The project includes a comprehensive CI/CD pipeline implemented with GitHub Actions that ensures 
code quality and reliability through automated testing, linting, and formatting checks.

#### GitHub Actions Workflows

**Test, Lint, Format Workflow** (`.github/workflows/test.yml`)

The workflow includes four parallel jobs:
1. **`ci-lint`**: Static code analysis using `ruff` and `mypy` type checking
2. **`ci-fmt-check`**: Code formatting verification with `ruff`
3. **`ci-unit`**: Unit test execution with `pytest`
4. **`ci-integration`**: Integration test execution with `pytest`

## 🚀 Getting Started

### Setting up the environment

1. Clone the repository
```bash
$ git clone https://github.com/gmyrianthous/ai-assistant.git
$ cd ai-assistant
```

2. Create and activate a virtual enviroment:
```bash
# optional: install uv
# osx/linux
$ curl -LsSf https://astral.sh/uv/install.sh | sh
# windows
$ powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies, and pre-commit hooks
$ make setup
```

3. Copy the sample environment file
```bash
$ cp .env.example .env
```

4. Update the content of the environment file using your configuration/keys etc. 

### Development

#### Running the tests

```bash
# Run all tests
$ make test

# Run unit tests only
$ make test-unit

# Run integration tests only
$ make test-integration
```

#### Working with database migrations
The source code utilises Alembic to manage and perform database migrations in an effective way. 

##### Creating a new database migration

```bash
# Spin up the docker container if not running already
$ make up

# Create a new revision with alembic
$ make migration-create revision_name="create table xyz"
```
If executed successfully, the new version should be located under `migration/versions` path. 

#### Applying database migrations

```bash
# Spin up the docker container if not running already
$ make up

# Run the migrations
$ make migration-run
```

## 📊 Evaluations


## 🔎 Monitoring & Observability
