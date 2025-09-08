FROM python:3.13 AS requirements-stage

WORKDIR /tmp

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/usr/local/

COPY ./pyproject.toml ./uv.lock* /tmp/

RUN --mount=type=cache,target=/root/.cache \
    uv sync --locked --no-dev

FROM python:3.13-slim AS prod

COPY --from=requirements-stage /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=requirements-stage /usr/local/bin/ /usr/local/bin/

RUN adduser worker
USER worker

WORKDIR /home/worker/app
COPY --chown=worker:worker . .

ENV PATH="/home/worker/.local/bin:/usr/local/bin/:${PATH}"