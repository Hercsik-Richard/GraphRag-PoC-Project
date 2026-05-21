# Multi-stage build for GraphRAG Backend

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend files
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy rest of frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Build Python dependencies
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY backend/pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --no-dev --no-install-project

# Stage 3: Backend tests
FROM python:3.12-slim AS backend-test

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and install runtime + dev dependencies
COPY backend/pyproject.toml ./
RUN uv venv /opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --no-install-project

# Copy application, scripts, samples, and tests
COPY .env.example README.md docker-compose.yml ./
COPY docs/ ./docs/
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY backend/samples/ ./samples/
COPY backend/tests/ ./tests/

# Create necessary directories
RUN mkdir -p ragtest/input ragtest/output ragtest/cache logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Initialize GraphRAG config from test environment, then run pytest
CMD ["sh", "-c", "uv run scripts/init_graphrag.py && uv run pytest"]

# Stage 4: Runtime
FROM python:3.12-slim AS runtime

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency file for uv
COPY backend/pyproject.toml ./

# Copy application code
COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY backend/samples/ ./samples/
COPY backend/ragtest/ ./ragtest/

# Copy frontend build to match local structure (../frontend/dist from /app)
COPY --from=frontend-builder /frontend/dist /frontend/dist

# Create necessary directories
RUN mkdir -p ragtest/input ragtest/output ragtest/cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run --no-dev python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Initialize GraphRAG config from runtime environment, then run application
CMD ["sh", "-c", "uv run --no-dev scripts/init_graphrag.py && exec uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port 8000"]
