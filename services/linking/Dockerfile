# syntax=docker/dockerfile:1
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# ENV choices:
# - DEBIAN_FRONTEND=noninteractive: Prevents interactive prompts during package installation.
# - PYTHONUNBUFFERED=1: Ensures Python logs are sent straight to terminal (useful for docker logs).
# - PYTHONDONTWRITEBYTECODE=1: Prevents unnecessary .pyc files in the container.
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

# Install Python 3.12 via PPA and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3.12-venv python3.12-dev \
    git unzip wget ssh-client build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up the Virtual Environment
RUN python3.12 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

WORKDIR /app

# Move into the project
WORKDIR /app/chnobli/nla
COPY src/ src/
COPY configs/ configs/
COPY scripts/ scripts/
COPY tests/ tests/
COPY utility/ utility/
COPY data/ data/
COPY main.py pyproject.toml .env_template README.md .

# Ensure uv uses the existing virtual environment and doesn't cache
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
# Install dependencies
RUN uv sync --no-dev --no-cache

# Get models
WORKDIR /app/chnobli/nla/models
COPY models/* ./
RUN if [ -z "$(ls -A . 2>/dev/null)" ]; then \
      echo "No models found in local directory. Start Download..." && \
        wget -O ner-bio.zip https://www.research-collection.ethz.ch/bitstreams/5be21deb-f852-4317-b428-162326e2a741/download && \
            unzip ner-bio.zip && \
            rm ner-bio.zip \
        wget -O ner-det.zip https://www.research-collection.ethz.ch/bitstreams/370809dd-190b-4687-87e6-73e42367dee1/download && \
            unzip ner-det.zip && \
            rm ner-det.zip\
    else \
      echo "Using local models from ./models/*, skip download."; \
    fi
WORKDIR /app/chnobli/nla

# Default command (can be overridden in docker-compose)
CMD ["tail", "-f", "/dev/null"]
