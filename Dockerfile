FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .

CMD ["uv", "run", "dictator/dictator.py"]
