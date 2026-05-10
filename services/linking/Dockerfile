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

# Install Python 3.11 via PPA and system dependencies
# This is much faster than compiling from source.
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

# Use BuildKit secrets to clone the repository securely.
# The key is never stored in the image layers.
RUN git clone git@github.com:eth-library/CHNOBLi.git

# Move into the repository
WORKDIR /app/nla

# Ensure uv uses the existing virtual environment and doesn't cache
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
RUN uv sync --no-dev --no-cache

# Download models and install Python dependencies
RUN wget -O ner-bio.zip https://www.research-collection.ethz.ch/bitstreams/5be21deb-f852-4317-b428-162326e2a741/download && \
    unzip ner-bio.zip && \
    rm ner-bio.zip

RUN wget -O ner-det.zip https://www.research-collection.ethz.ch/bitstreams/370809dd-190b-4687-87e6-73e42367dee1/download && \
    unzip ner-det.zip && \
    rm ner-det.zip

# Default command (can be overridden in docker-compose)
CMD ["tail","-f", "/dev/null"]
