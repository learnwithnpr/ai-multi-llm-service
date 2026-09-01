# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install runtime dependencies only (no build tools needed for these wheels).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY main.py .
COPY app/ ./app/

# Non-root user for production
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Scale workers with CPU cores in production, e.g. --workers 4
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
