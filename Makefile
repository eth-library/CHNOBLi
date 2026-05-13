# Auto-detect host user identity so that files created in mounted volumes
# are owned by the user running make, not by root or an arbitrary UID.
UID := $(shell id -u)
GID := $(shell id -g)

COMPOSE_BUILD  = docker-compose-dev.yml
IMAGE_NAME     = linking:v0.1

# Directories that will be mounted into the container.
# Pre-creating them ensures they are owned by the current user, not root.
PRIVATE_DIRS = private/input private/output private/logs

.PHONY: help build up down logs shell shell-root webui-build webui-up webui-down _setup_dirs

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup targets:"
	@echo "  setup        Interactive setup (choose between minimal or full local)"
	@echo "  import-data  Interactive data import (Wikidata, GND, Milvus)"
	@echo ""
	@echo "Development targets (builds image from source):"
	@echo "  build        Build the Docker image"
	@echo "  up           Start the container (dev)"
	@echo "  down         Stop and remove the container (dev)"
	@echo "  logs         Tail container logs"
	@echo "  shell        Open a bash shell in the running container"
	@echo "  shell-root   Open a root bash shell in the running container"
	@echo "  webui-build  Build the web UI image"
	@echo "  webui-up     Start the web UI (http://localhost:8501)"
	@echo "  webui-down   Stop the web UI"

# --- Setup ---

setup:
	chmod +x maintenance/setup.sh
	./maintenance/setup.sh

import-data:
	chmod +x maintenance/import_data.sh
	./maintenance/import_data.sh

# --- Development ---

build:
	UID=$(UID) GID=$(GID) docker compose -f $(COMPOSE_BUILD) build

up: _setup_dirs
	UID=$(UID) GID=$(GID) docker compose up -d linking streamlit_ui

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker exec -it linking bash

shell-root:
	docker exec -u 0 -it linking bash

webui-build:
	docker compose build streamlit_ui

webui-up: _setup_dirs
	docker compose up -d streamlit_ui

webui-down:
	docker compose stop streamlit_ui

# Pre-create mounted directories as the current user so Docker does not
# create them as root when starting the container for the first time.
_setup_dirs:
	mkdir -p $(PRIVATE_DIRS)
