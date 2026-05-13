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

# Create a non-root user 'appuser' (UID 1000).
# The runtime user is set via docker-compose (user: "${UID}:${GID}"),
# so the host user's UID/GID governs file ownership on mounted volumes.
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Prepare directories and hand them over to appuser for the build
RUN mkdir -p /app /opt/venv && \
    chown -R appuser:appuser /app /opt/venv

# Install uv for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv
ENV PATH="/uv/bin:$PATH"

# Copy the entrypoint script (needs root to write to /usr/local/bin)
COPY services/linking/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to the non-root user for all application setup
USER appuser

# Set up the virtual environment as appuser
RUN python3.12 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Move into the project
WORKDIR /app/chnobli/nla
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser configs/ configs/
COPY --chown=appuser:appuser scripts/ scripts/
COPY --chown=appuser:appuser tests/ tests/
COPY --chown=appuser:appuser utility/ utility/
COPY --chown=appuser:appuser data/ data/
COPY --chown=appuser:appuser main.py pyproject.toml .env_template README.md .

# Ensure uv uses the existing virtual environment and doesn't cache
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
# Install dependencies
RUN uv sync --no-dev --no-cache --no-install-project

# Get models
WORKDIR /app/chnobli/nla/models
COPY models/* ./
# Copy maintenance tools temporarily for the build
COPY --chown=appuser:appuser maintenance/ /tmp/maintenance/
#RUN python maintenance/resave_models.py --in-place

# Use the resolver to get the latest bitstream URLs
RUN if [ ! -f "ner-bio.pt" ]; then \
      echo "ner-bio.pt not found. Resolving from DOI..." && \
      URL=$(python3 /tmp/maintenance/resolve_doi.py --component models --file ner-bio) && \
      wget -O ner-bio.pt "$URL"; \
    fi

RUN if [ ! -f "ner-det.pt" ]; then \
      echo "ner-det.pt not found. Resolving from DOI..." && \
      URL=$(python3 /tmp/maintenance/resolve_doi.py --component models --file ner-det) && \
      wget -O ner-det.pt "$URL"; \
    fi

RUN rm -rf /tmp/maintenance
WORKDIR /app/chnobli/nla

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command (can be overridden in docker-compose)
CMD ["tail", "-f", "/dev/null"]
