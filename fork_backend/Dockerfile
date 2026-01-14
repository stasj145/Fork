# --- Stage 1: Builder ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

# Install compilation tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
# Ensure we use the virtualenv for subsequent pip commands
ENV PATH="/opt/venv/bin:$PATH"

# 1. Install CPU-only Torch first (Massive size saver)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install your project
COPY pyproject.toml ./
# This installs your project and all dependencies into the venv
RUN pip install --no-cache-dir .

# --- Stage 2: Final ---
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install runtime-only system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy your source code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Ensure the app uses the virtualenv
    PATH="/opt/venv/bin:$PATH"

# Non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Now 'uvicorn' will be found in /opt/venv/bin because of the updated PATH
CMD ["uvicorn", "main:uvicorn_entry", "--host", "0.0.0.0", "--port", "8000", "--factory"]