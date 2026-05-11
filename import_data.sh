#!/bin/bash

set -e

SERVICES_DIR="services"
ES_DIR="$SERVICES_DIR/CHNOBLi-elasticsearch"
MILVUS_DIR="$SERVICES_DIR/CHNOBLi-vectordb"
ROOT_ENV="$(pwd)/.env"

echo "=========================================="
echo "      CHNOBLi Data Import Wizard"
echo "=========================================="
echo ""
echo "Note: Ensure your databases are running before proceeding!"
echo ""

# Helper to check if Elasticsearch is up
check_es() {
    echo "[*] Checking if Elasticsearch is reachable..."
    if ! curl -k -s "https://localhost:9200" > /dev/null; then
        echo "Error: Elasticsearch is not reachable at https://localhost:9200."
        echo "Please make sure your containers are started and healthy."
        exit 1
    fi
}

# Helper to set up virtual environment
# Priority: uv -> conda -> python3.12 -m venv
setup_venv() {
    local target_dir=$1
    local install_cmd=$2 # "pip install -r requirements.txt" or "pip install -e ."
    
    echo "[*] Setting up Python environment in $target_dir..."
    cd "$target_dir"
    
    # 0. Skip if already exists
    if [ -d ".venv" ]; then
        echo "    -> Environment .venv already exists, activating..."
        source .venv/bin/activate
        return 0
    fi
    if [ -d ".conda_env" ]; then
        echo "    -> Environment .conda_env already exists, activating..."
        CONDA_PATH=$(conda info --base)
        source "$CONDA_PATH/etc/profile.d/conda.sh"
        conda activate ./.conda_env
        return 0
    fi

    # 1. Try uv
    if command -v uv >/dev/null 2>&1; then
        echo "    -> Using uv"
        if [ -f "pyproject.toml" ]; then
            uv sync
            source .venv/bin/activate
        else
            uv venv .venv --python 3.12
            source .venv/bin/activate
            uv pip install -r requirements.txt
        fi
        return 0
    fi
    
    # 2. Try conda
    if command -v conda >/dev/null 2>&1; then
        echo "    -> Using conda"
        # Create a local conda environment in .conda_env
        conda create -y -p ./.conda_env python=3.12
        # To activate conda in a script we need this:
        CONDA_PATH=$(conda info --base)
        source "$CONDA_PATH/etc/profile.d/conda.sh"
        conda activate ./.conda_env
        $install_cmd
        return 0
    fi
    
    # 3. Try python3.12
    if command -v python3.12 >/dev/null 2>&1; then
        echo "    -> Using python3.12 -m venv"
        python3.12 -m venv .venv
        source .venv/bin/activate
        $install_cmd
        return 0
    fi

    # Fallback to python3 if it's 3.12+
    if command -v python3 >/dev/null 2>&1; then
        PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [ "$PY_VER" == "3.12" ]; then
            echo "    -> Using python3 -m venv (version $PY_VER)"
            python3 -m venv .venv
            source .venv/bin/activate
            $install_cmd
            return 0
        fi
    fi
    
    echo "Error: Could not find uv, conda, or python 3.12 to create environment."
    exit 1
}

echo "What data would you like to import?"
echo "1) Elasticsearch: Wikidata (People)"
echo "2) Elasticsearch: GND (People)"
echo "3) Milvus: Vector Embeddings"
echo "4) Import All"
echo "q) Quit"
echo ""
read -p "Choose an option: " IMPORT_CHOICE

import_es_wikidata() {
    check_es
    echo ""
    echo ">>> Importing Wikidata to Elasticsearch..."
    if [ ! -d "$ES_DIR" ]; then
        echo "Error: $ES_DIR not found. Did you run 'make setup'?"
        exit 1
    fi
    cd "$ES_DIR"
    # Ensure sub-repo has a .env if it doesn't, or link to root one
    if [ ! -f ".env" ]; then
        echo "[*] Creating local .env for Elasticsearch service..."
        cp .env_template .env
        # Try to sync credentials from root .env if possible
        if [ -f "$ROOT_ENV" ]; then
            USER_VAL=$(grep ELASTIC_USERNAME "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
            PASS_VAL=$(grep ELASTIC_PASSWORD "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
            if [ ! -z "$USER_VAL" ]; then sed -i "s|^ELASTIC_USERNAME=.*|ELASTIC_USERNAME=$USER_VAL|" .env; fi
            if [ ! -z "$PASS_VAL" ]; then sed -i "s|^ELASTIC_PASSWORD=.*|ELASTIC_PASSWORD=$PASS_VAL|" .env; fi
        fi
    fi
    
    # Go to ES dir and setup env
    setup_venv "$ES_DIR" "pip install -r requirements.txt"
    
    python utils/wikidata_load_to_elasticsearch.py
    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - > /dev/null
}

import_es_gnd() {
    check_es
    echo ""
    echo ">>> Importing GND to Elasticsearch..."
    if [ ! -d "$ES_DIR" ]; then
        echo "Error: $ES_DIR not found. Did you run 'make setup'?"
        exit 1
    fi
    cd "$ES_DIR"
    # Same .env check
    if [ ! -f ".env" ]; then
        echo "[*] Creating local .env for Elasticsearch service..."
        cp .env_template .env
        if [ -f "$ROOT_ENV" ]; then
            USER_VAL=$(grep ELASTIC_USERNAME "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
            PASS_VAL=$(grep ELASTIC_PASSWORD "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
            if [ ! -z "$USER_VAL" ]; then sed -i "s|^ELASTIC_USERNAME=.*|ELASTIC_USERNAME=$USER_VAL|" .env; fi
            if [ ! -z "$PASS_VAL" ]; then sed -i "s|^ELASTIC_PASSWORD=.*|ELASTIC_PASSWORD=$PASS_VAL|" .env; fi
        fi
    fi

    # Go to ES dir and setup env
    setup_venv "$ES_DIR" "pip install -r requirements.txt"

    python utils/gnd_load_to_elasticsearch.py
    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - > /dev/null
}

import_milvus() {
    echo ""
    echo ">>> Importing Data to Milvus..."
    if [ ! -d "$MILVUS_DIR" ]; then
        echo "Error: $MILVUS_DIR not found. Did you run 'make setup'?"
        exit 1
    fi

    # The research collection URL
    MILVUS_DATA_URL="https://www.research-collection.ethz.ch/bitstreams/f305c48b-7f2a-431b-93f4-3e9f4e24242e/download" # Placeholder or known ID
    DATA_FOLDER="$MILVUS_DIR/gnd_de_snowflakearctic"
 
    if [ ! -d "$DATA_FOLDER" ]; then
        echo "[*] Milvus data not found locally. Attempting to download..."
        mkdir -p "$DATA_FOLDER"
        cd "$DATA_FOLDER"
        
        # Note: If this fails, it might be because the bitstream ID changed or server is down
        if ! curl -L -A "Mozilla/5.0" -o milvus_dump.zip "$MILVUS_DATA_URL"; then
            echo "Error: Automated download failed."
            echo "Please download the data manually from: http://hdl.handle.net/20.500.11850/799813"
            echo "Unzip it and place the contents in: $DATA_FOLDER"
            exit 1
        fi

        # Check if the downloaded file is actually a zip
        if ! file milvus_dump.zip | grep -q "Zip archive data"; then
            echo "Error: The downloaded file is not a valid zip archive."
            echo "The server might be returning an error page (HTTP 500)."
            echo "Please check the link manually: http://hdl.handle.net/20.500.11850/799813"
            rm milvus_dump.zip
            exit 1
        fi

        echo "[*] Extracting data..."
        if ! unzip milvus_dump.zip; then
            echo "Error: Extraction failed."
            rm milvus_dump.zip
            exit 1
        fi
        rm milvus_dump.zip
        cd - > /dev/null
    else
        echo "[*] Milvus data already exists in $DATA_FOLDER. Skipping download."
    fi

    # Setup env for Milvus
    setup_venv "$MILVUS_DIR" "pip install -e ."
    
    echo "Running import..."
    milvus_dump import -d ./gnd_de_snowflakearctic
    
    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - > /dev/null
}

case $IMPORT_CHOICE in
    1)
        import_es_wikidata
        ;;
    2)
        import_es_gnd
        ;;
    3)
        import_milvus
        ;;
    4)
        import_es_wikidata
        import_es_gnd
        import_milvus
        ;;
    q)
        exit 0
        ;;
    *)
        echo "Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "Import process finished!"
