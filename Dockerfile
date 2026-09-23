# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /fast-api-workdir
ENV UV_PYTHON_DOWNLOADS=0

RUN uv venv


COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    VIRTUAL_ENV=/fast-api-workdir/.venv uv sync --frozen --no-dev --no-install-project


FROM python:3.12-slim
WORKDIR /fast-api-workdir


COPY --from=builder /fast-api-workdir/.venv /fast-api-workdir/.venv


COPY . .

ENV PATH="/fast-api-workdir/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]