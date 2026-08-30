# 🤖💬 AI Assistant Python Template
This is a production-ready Python template that can be used to ship agentic systems with FastAPI
and Agent Development Kit (ADK). The template aims to provide a boilerplate solution with 
batteries included:
- API (FastAPI)
- AI Agents (Agent Development Kit)
- User Interface (served through ADK's `adk web`)
- Monitoring & Observability (Grafana, Langfuse)
- Model Evaluations (Langfuse)
- CI/CD (GitHub Actions)


## 🌟 Features

### ⚙️ API
The backend implementation exposes endpoints that facilitate:
- Session Management (REST, under `/api/v1/chatbot`)
- Chat via the [AG-UI protocol](https://docs.ag-ui.com) (`POST /api/v1/chat`)

Chat interactions are served over AG-UI, the open agent↔user interaction protocol:
the endpoint accepts a `RunAgentInput` payload and streams standard AG-UI events
(`RUN_STARTED`, `TEXT_MESSAGE_*`, `TOOL_CALL_*`, `RUN_FINISHED`, ...) as Server-Sent
Events. Any AG-UI-compatible client (e.g. [CopilotKit](https://www.copilotkit.ai))
can consume it out of the box; the AG-UI `threadId` maps directly to the ADK session
id, so conversations are also visible through the session endpoints.

For local development, a minimal browser chat client speaking AG-UI is served at
http://localhost:8080/chat — handy for talking to the agent without setting up a
full frontend.

> The swagger documentation for the available endpoints can be accessed on 
> https://localhost:8080/docs

### 💾 Data Store


### 💡AI


### 🖥️ User Interface
 It is possible to run agents in isolation and interact with them via a User Interface, 
 specifically using `adk web` that is part of the Agent Development Kit.

  #### Development Architecture
  The codebase is structured to support a **dual-mode architecture** that enables both isolated 
  agent development and production service deployment:

  ```shell
  ai_assistant/services/ai/adk/agents/
  └── weather_assistant/
      ├── init.py
      └── agent.py
  ```

  This structure provides several key advantages:

  **1. Isolated Development & Testing**
  - Develop and test agents independently without running the full API service
  - Rapidly iterate on prompts, tools, and configurations using the interactive UI
  - Debug agent behavior in real-time with immediate visual feedback

  **2. Zero Configuration Deployment**
  - Agents developed locally are automatically discovered by the service layer
  - No code changes needed when moving from development to production
  - The same agent definition works in both `adk web` and the FastAPI service

  **3. Consistent Agent Interface**
  - Single source of truth for agent configuration (prompts, models, tools)
  - Reduces discrepancies between development and production environments

  **4. Streamlined Workflow**
  - Test agent responses and tool execution in `adk web`
  - Once satisfied, the agent is ready for API integration without modification
  - Session state and conversation history work identically in both modes

  #### Running ADK Web

  To spin up the ADK web User Interface, simply run the following command from the top-level 
  directory:

  ```shell
  # $ pwd
  # path/to/ai-assistant
  $ make adk-web
  ```

  The UI will launch at http://localhost:8000 where you can:
  - Chat with agents interactively
  - View tool execution and results
  - Inspect session state and conversation history
  - Test different prompts and configurations in real-time

  This development experience ensures that what you build and test locally will behave identically 
  when deployed as a service.

> **_Note:_**  You must use the `make adk-web` command instead of running adk web directly from 
> the CLI, via `adk web`. The Makefile configures both the PYTHONPATH environment variable and 
> the correct agents directory path to ensure agents are discoverable. Running adk web without this
> configuration will result in your agents not being found.

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

### Local environment at a glance

Spin up everything (all docker services + Langfuse prompt seeding + GrowthBook
bootstrap), then run the Postman smoke tests against the live API, with a single
command:

```bash
$ make local
```

> Requires an authenticated `gcloud` session (the api image build pulls from a
> private registry) and a `.env` file (`cp .env.example .env`). To run only the
> supporting services without the api container:
> `docker compose up -d --wait db langfuse-web langfuse-worker growthbook`

Once up, these are all the local services, links and credentials:

| Service | URL | Credentials |
| --- | --- | --- |
| API (FastAPI) | http://localhost:8080 (Swagger: [/docs](http://localhost:8080/docs)) | — |
| Browser chat client (AG-UI) | http://localhost:8080/chat | — |
| AG-UI chat endpoint | `POST` http://localhost:8080/api/v1/chat | — |
| ADK web UI (`make adk-web`) | http://localhost:8000 | — |
| Langfuse (tracing & prompts) | http://localhost:3001 | `dev@example.com` / `langfuse-local` · API keys `pk-lf-local` / `sk-lf-local` |
| GrowthBook (flags & experiments) | http://localhost:3002 (SDK API: http://localhost:3101) | `dev@example.com` / `growthbook-local` · SDK key written to `.env` by the seed |
| Postgres (app database) | `localhost:5432` | `postgres` / `postgres` · db `ai_assistant` |
| MinIO console (Langfuse storage) | http://localhost:9091 | `minio` / `miniosecret` |
| Postman smoke tests (`make postman`) | collection: [`postman/`](postman/) | — |

All credentials are throwaway values for local development only.

> Port clashes: if another local project already binds a port (e.g. a different
> Postgres on 5432), stop it first or adjust the port mapping in `docker-compose.yml`.

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

#### API smoke tests (Postman / newman)
A Postman collection covering all endpoints lives in `postman/`, built around a
`base_url` variable with per-target environment files (`postman/environments/`).
Run it headlessly with [newman](https://github.com/postmanlabs/newman) — fully local,
no Postman account needed:

```bash
# Dockerised (no install), against the API on localhost:8080
$ make postman

# Or with node installed, using the local environment file
$ npx newman run postman/ai-assistant.postman_collection.json \
    -e postman/environments/local.postman_environment.json
```

The collection chains requests (the created `session_id` feeds the follow-up
requests) and asserts on every response, so it doubles as an end-to-end smoke
suite. It can also be imported into the Postman app directly.

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

#### Running Langfuse locally
The docker compose file includes a self-hosted [Langfuse](https://langfuse.com) stack
(web + worker + ClickHouse + Redis + MinIO + a dedicated Postgres) for local development.

```bash
# Spin up Langfuse (and its dependencies)
$ docker compose up -d langfuse-web langfuse-worker

# Seed the prompts the app fetches at startup (orchestrator + agents)
$ make langfuse-seed
```

On first boot, an organisation, project, user and API keys are provisioned automatically
(headless init), matching the defaults in `.env.example`:

- UI: http://localhost:3001 (login: `dev@example.com` / `langfuse-local`)
- API keys: `pk-lf-local` / `sk-lf-local`

> The `api` service reaches Langfuse at `http://langfuse-web:3000` inside the compose
> network; processes running on the host (e.g. `adk web`, the seed script) use
> `http://localhost:3001` from `.env`.

#### Feature flags & experimentation (GrowthBook)
The docker compose file also includes a self-hosted [GrowthBook](https://www.growthbook.io)
instance for feature flags and A/B experiments (e.g. testing prompt variations):

```bash
$ docker compose up -d growthbook

# Bootstrap everything headlessly (no UI signup needed)
$ make growthbook-seed
```

The seed script provisions the whole setup idempotently:
- the admin account (`dev@example.com` / `growthbook-local`, UI at http://localhost:3002)
- a Python SDK connection, with the client key written into `.env`
- the `orchestrator-prompt-label` string feature with a **50/50 experiment** between
  the default prompt label (= `ENVIRONMENT`) and a `-b` variant label
- the variant `orchestrator` prompt in Langfuse (label `<ENVIRONMENT>-b`)

The feature's value is the **Langfuse prompt label** served to each user, so the
experiment A/B tests orchestrator prompt variants with consistent per-user bucketing.
Flags fail open: if GrowthBook is unreachable or a label doesn't exist in Langfuse,
the default prompt (label = `ENVIRONMENT`) is served.

## 📊 Evaluations


## 🔎 Monitoring & Observability
