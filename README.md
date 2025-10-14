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
- Session Management 
- Interactions between the chatbot and the end user 

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

> **_Note:_**  You must use the make adk-web command instead of running adk web directly from 
> the CLI. The Makefile configures both the PYTHONPATH environment variable and the correct 
> agents directory path to ensure agents are discoverable. Running adk web without this
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
