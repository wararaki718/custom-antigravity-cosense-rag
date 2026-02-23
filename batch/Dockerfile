FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --no-cache

COPY . .

# Batch might be run as a script
CMD ["uv", "run", "main.py"]
