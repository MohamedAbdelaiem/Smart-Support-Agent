FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compilation & postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Copy dependency specifications
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir .

# Copy application source code & static assets
COPY src/ src/
COPY frontend/ frontend/
COPY data/ data/
COPY scripts/ scripts/

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
