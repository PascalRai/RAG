# FastAPI stage (light image)
FROM python:3.11-slim AS fastapi

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Minimal OS deps for runtime + building small wheels
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only light/runtime dependencies for FastAPI.
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy application code
COPY . .

# Default CMD (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Celery stage (inherits FastAPI stage and adds heavy deps)
FROM fastapi AS celery

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxcb1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Install heavy dependencies for celery/ingestion (e.g., transformers, torch, CUDA wheels, etc.)
RUN pip install docling

# Keep app files from previous stage (already copied)
# No CMD here; docker-compose overrides command for celery worker.