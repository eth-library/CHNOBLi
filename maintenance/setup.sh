#!/bin/bash

# Repository URLs
ES_REPO="https://github.com/eth-library/CHNOBLi-elasticsearch.git"
MILVUS_REPO="https://github.com/eth-library/CHNOBLi-vectordb.git"
EMBEDDING_ENGINE_REPO="https://gitlab.ethz.ch/library/adl/Machine_learning_platform/embeddings-engine"
EMBEDDING_BACKEND_REPO="https://gitlab.ethz.ch/library/adl/Machine_learning_platform/embeddings-backend"

# Paths (Relative to the script location)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$ROOT_DIR/.env"
ENV_TEMPLATE="$ROOT_DIR/.env_template"
SERVICES_DIR="$ROOT_DIR/services"

echo "=========================================="
echo "      CHNOBLi Project Setup Wizard"
echo "=========================================="
echo ""

# 1. Create .env if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo "[*] Creating .env file from template..."
    cp "$ENV_TEMPLATE" "$ENV_FILE"
else
    echo "[*] .env file already exists."
fi

echo ""
echo "How would you like to set up the databases?"
echo "1) Minimal Setup (Use remote APIs / existing instances)"
echo "2) Full Local Setup (Download and run local Elasticsearch & Milvus)"
echo ""
read -p "Choose an option [1-2]: " SETUP_CHOICE

case $SETUP_CHOICE in
1)
    echo ""
    echo ">>> Minimal Setup Selected"
    echo "Please edit the .env file to provide your remote API credentials."
    echo ""
    ;;
2)
    echo ""
    echo ">>> Full Local Setup Selected"

    # Create services directory if it doesn't exist
    mkdir -p "$SERVICES_DIR"

    # Clone Elasticsearch repo
    if [ ! -d "$SERVICES_DIR/CHNOBLi-elasticsearch" ]; then
        echo "[*] Cloning CHNOBLi-elasticsearch..."
        git clone "$ES_REPO" "$SERVICES_DIR/CHNOBLi-elasticsearch"
    else
        echo "[*] CHNOBLi-elasticsearch already exists in $SERVICES_DIR."
    fi

    # Clone Milvus repo
    if [ ! -d "$SERVICES_DIR/CHNOBLi-vectordb" ]; then
        echo "[*] Cloning CHNOBLi-vectordb..."
        git clone "$MILVUS_REPO" "$SERVICES_DIR/CHNOBLi-vectordb"
    else
        echo "[*] CHNOBLi-vectordb already exists in $SERVICES_DIR."
    fi

    # Clone Embedding Engine
    if [ ! -d "$SERVICES_DIR/embedding-engine" ]; then
        echo "[*] Cloning embedding-engine..."
        git clone "$EMBEDDING_ENGINE_REPO" "$SERVICES_DIR/embedding-engine"
    else
        echo "[*] embedding-engine already exists in $SERVICES_DIR."
    fi

    # Clone Embeddings Backend
    if [ ! -d "$SERVICES_DIR/embeddings-backend" ]; then
        echo "[*] Copying embeddings-backend..."
        git clone -b "apelloni/chnobli" "$EMBEDDING_BACKEND_REPO" "$SERVICES_DIR/embeddings-backend"
    else
        echo "[*] embeddings-backend already exists in $SERVICES_DIR."
    fi

    # Dynamically inject the local requirement
    REQ_FILE="$ROOT_DIR/requirements.txt"
    if ! grep -q "embedding-engine" "$REQ_FILE"; then
        echo "[*] Injecting local embedding-engine dependency into requirements.txt"
        echo "embedding-engine @ file://./services/embedding-engine" >>"$REQ_FILE"
    fi

    # Update PATH_TO_CA_CERT in .env
    NEW_CERT_PATH="services/CHNOBLi-elasticsearch/secrets/certs/ca/ca.crt"
    echo "[*] Updating PATH_TO_CA_CERT in .env..."

    # Use sed to replace the path. Handle both single and double quotes.
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^PATH_TO_CA_CERT=.*|PATH_TO_CA_CERT=\"$NEW_CERT_PATH\"|" "$ENV_FILE"
    else
        sed -i "s|^PATH_TO_CA_CERT=.*|PATH_TO_CA_CERT=\"$NEW_CERT_PATH\"|" "$ENV_FILE"
    fi

    # Automate Elasticsearch setup
    echo ""
    echo "[*] Configuring and setting up Elasticsearch containers..."
    ES_SUB_DIR="$SERVICES_DIR/CHNOBLi-elasticsearch"
    if [ -d "$ES_SUB_DIR" ]; then
        cd "$ES_SUB_DIR"
        if [ ! -f ".env" ]; then
            cp .env_template .env
        fi
        # Sync credentials from root .env
        ROOT_ENV_PATH="$ROOT_DIR/.env"
        if [ -f "$ROOT_ENV_PATH" ]; then
            USER_VAL=$(grep ELASTIC_USERNAME "$ROOT_ENV_PATH" | cut -d'=' -f2 | tr -d '"')
            PASS_VAL=$(grep ELASTIC_PASSWORD "$ROOT_ENV_PATH" | cut -d'=' -f2 | tr -d '"')
            if [ ! -z "$USER_VAL" ]; then sed -i "s|^ELASTIC_USERNAME=.*|ELASTIC_USERNAME=\"$USER_VAL\"|" .env; fi
            if [ ! -z "$PASS_VAL" ]; then sed -i "s|^ELASTIC_PASSWORD=.*|ELASTIC_PASSWORD=\"$PASS_VAL\"|" .env; fi
        fi
        # Run docker compose setup
        echo "[*] Generating certificates and keystore..."
        docker compose -f docker-compose.setup.yml run --rm certs
        docker compose -f docker-compose.setup.yml run --rm keystore
        cd - >/dev/null
    fi

    # Automate embeddings-backend setup
    echo ""
    echo "[*] Configuring embeddings-backend environment..."
    EMB_SUB_DIR="$SERVICES_DIR/embeddings-backend"
    if [ -d "$EMB_SUB_DIR" ]; then
        cd "$EMB_SUB_DIR"
        ROOT_ENV_PATH="$ROOT_DIR/.env"
        if [ -f "$ROOT_ENV_PATH" ]; then
            # Extract token value from root .env
            TOKEN_EMB=$(grep "^GITLAB_TOKEN_EMBEDDINGS=" "$ROOT_ENV_PATH" | cut -d'=' -f2- | tr -d '"' | tr -d "'")

            if [ -f ".env.chnobli" ]; then
                if [ ! -z "$TOKEN_EMB" ]; then
                    if [[ "$OSTYPE" == "darwin"* ]]; then
                        sed -i '' "s|^GITLAB_TOKEN_EMBEDDINGS=.*|GITLAB_TOKEN_EMBEDDINGS=\"$TOKEN_EMB\"|" .env.chnobli
                    else
                        sed -i "s|^GITLAB_TOKEN_EMBEDDINGS=.*|GITLAB_TOKEN_EMBEDDINGS=\"$TOKEN_EMB\"|" .env.chnobli
                    fi
                fi
            fi
        fi
        cd - >/dev/null
    fi

    echo ""
    echo "=========================================="
    echo "Setup complete! To start your local services:"
    echo ""
    echo "1. Start Elasticsearch:"
    echo "   cd $SERVICES_DIR/CHNOBLi-elasticsearch && docker compose up -d"
    echo ""
    echo "2. Start Milvus:"
    echo "   cd $SERVICES_DIR/CHNOBLi-vectordb && docker compose up -d"
    echo ""
    echo "3. Start Embeddings Backend (Wait for Milvus to be ready):"
    echo "   * IMPORTANT: Ensure your GITLAB_TOKEN_EMBEDDINGS is defined in the root .env before running setup.sh"
    echo "   cd $SERVICES_DIR/embeddings-backend && docker compose -f docker-compose.chnobli.yml --env-file .env.chnobli up -d --build"
    echo ""
    echo "After they are running, you can proceed with the main project."
    echo "=========================================="

    echo ""
    read -p "Would you like to run the data import/download script now? [y/N]: " IMPORT_CHOICE
    if [[ "$IMPORT_CHOICE" =~ ^[Yy]$ ]]; then
        echo ""
        echo "[*] Launching data import script..."
        chmod +x "$ROOT_DIR/maintenance/import_data.sh"
        "$ROOT_DIR/maintenance/import_data.sh"
    fi
    ;;
*)
    echo "Invalid choice. Setup aborted."
    exit 1
    ;;
esac

echo ""
echo "Done! You can now use 'make build' and 'make up' to start the main application."
