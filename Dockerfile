FROM python:3.11-slim-bookworm

# uv for fast, lockfile-based installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies from the lockfile first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the application
COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8585
CMD ["streamlit", "run", "--server.port", "8585", "--server.address", "0.0.0.0", "./streamlit_app.py"]
