#!/bin/bash

set -e

# Paths (Relative to the script location)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICES_DIR="$ROOT_DIR/services"
ES_DIR="$SERVICES_DIR/CHNOBLi-elasticsearch"
MILVUS_DIR="$SERVICES_DIR/CHNOBLi-vectordb"
ROOT_ENV="$ROOT_DIR/.env"

echo "=========================================="
echo "      CHNOBLi Data Import Wizard"
echo "=========================================="
echo ""
echo "Note: Ensure your databases are running before proceeding!"
echo ""

# Helper to resolve URLs from the registry
get_url() {
    local component=$1
    local file=$2
    python3 "$SCRIPT_DIR/resolve_doi.py" --component "$component" --file "$file"
}

# DOIs for reference (will be printed on error)
DOI_815="https://doi.org/10.3929/ethz-c-000799815"
DOI_811="https://doi.org/10.3929/ethz-c-000799811"
DOI_813="https://doi.org/10.3929/ethz-c-000799813"

# Helper to download a file with curl
download_file() {
    local url=$1
    local output=$2
    local description=$3
    echo "[*] Downloading $description..."
    if ! curl -L -A "Mozilla/5.0" -o "$output" "$url"; then
        echo "Error: Failed to download $description."
        exit 1
    fi
}

# Helper to check if Elasticsearch is up
check_es() {
    echo "[*] Checking if Elasticsearch is reachable..."
    if ! curl -k -s "https://localhost:9200" >/dev/null; then
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
echo "4) NER Models"
echo "5) Import All (DBs only)"
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
    fi
    # Always try to sync credentials from root .env if possible
    if [ -f "$ROOT_ENV" ]; then
        USER_VAL=$(grep ELASTIC_USERNAME "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
        PASS_VAL=$(grep ELASTIC_PASSWORD "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
        if [ ! -z "$USER_VAL" ]; then sed -i "s|^ELASTIC_USERNAME=.*|ELASTIC_USERNAME=\"$USER_VAL\"|" .env; fi
        if [ ! -z "$PASS_VAL" ]; then sed -i "s|^ELASTIC_PASSWORD=.*|ELASTIC_PASSWORD=\"$PASS_VAL\"|" .env; fi
    fi

    # Download data if missing
    if [ ! -f "wikidata_people_en.jsonl" ]; then
        URL=$(get_url "elasticsearch" "wikidata_people")
        download_file "$URL" "wikidata_people_en.zip" "Wikidata dump"
        unzip -o wikidata_people_en.zip
        rm wikidata_people_en.zip
    fi

    setup_venv "$ES_DIR" "pip install -r requirements.txt"

    python utils/wikidata_load_to_elasticsearch.py
    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - >/dev/null
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
    fi
    if [ -f "$ROOT_ENV" ]; then
        USER_VAL=$(grep ELASTIC_USERNAME "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
        PASS_VAL=$(grep ELASTIC_PASSWORD "$ROOT_ENV" | cut -d'=' -f2 | tr -d '"')
        if [ ! -z "$USER_VAL" ]; then sed -i "s|^ELASTIC_USERNAME=.*|ELASTIC_USERNAME=\"$USER_VAL\"|" .env; fi
        if [ ! -z "$PASS_VAL" ]; then sed -i "s|^ELASTIC_PASSWORD=.*|ELASTIC_PASSWORD=\"$PASS_VAL\"|" .env; fi
    fi

    # Download data if missing
    if [ ! -f "gnd_people.jsonl" ]; then
        URL=$(get_url "elasticsearch" "gnd_people")
        download_file "$URL" "gnd_people.zip" "GND dump"
        # The GND zip might contain persons_denormalized.jsonl
        unzip -o gnd_people.zip
        if [ -f "persons_denormalized.jsonl" ]; then
            mv persons_denormalized.jsonl gnd_people.jsonl
        fi
        rm gnd_people.zip
    fi

    # Go to ES dir and setup env
    setup_venv "$ES_DIR" "pip install -r requirements.txt"

    python utils/gnd_load_to_elasticsearch.py
    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - >/dev/null
}

import_milvus() {
    echo ""
    echo ">>> Importing Data to Milvus..."
    if [ ! -d "$MILVUS_DIR" ]; then
        echo "Error: $MILVUS_DIR not found. Did you run 'make setup'?"
        exit 1
    fi

    DATA_FOLDER="$MILVUS_DIR/gnd_de_snowflakearctic"

    if [ ! -d "$DATA_FOLDER" ]; then
        echo "[*] Milvus data not found locally. Attempting to download..."
        cd "$MILVUS_DIR"

        download_file "$(get_url "milvus" "part_1")" "gnd_de_snowflakearctic_1.zip" "Milvus dump part 1"
        download_file "$(get_url "milvus" "part_2")" "gnd_de_snowflakearctic_2.zip" "Milvus dump part 2"
        download_file "$(get_url "milvus" "part_3")" "gnd_de_snowflakearctic_3.zip" "Milvus dump part 3"

        echo "[*] Extracting data..."
        unzip -o "gnd_de_snowflakearctic_*.zip"
        rm gnd_de_snowflakearctic_*.zip
        cd - >/dev/null
    else
        echo "[*] Milvus data already exists in $DATA_FOLDER. Skipping download."
    fi

    # Setup env for Milvus
    setup_venv "$MILVUS_DIR" "pip install -e ."

    echo "Running import..."
    milvus_dump import -d ./gnd_de_snowflakearctic

    if [ -d ".venv" ]; then deactivate; elif [ -d ".conda_env" ]; then conda deactivate; fi
    cd - >/dev/null
}

import_models() {
    echo ""
    echo ">>> Downloading NER Models..."
    MODEL_DIR="$ROOT_DIR/models"
    mkdir -p "$MODEL_DIR"

    if [ ! -f "$MODEL_DIR/ner-bio.pt" ]; then
        download_file "$(get_url "models" "ner-bio")" "$MODEL_DIR/ner-bio.pt" "NER Bio model"
    fi
    if [ ! -f "$MODEL_DIR/ner-det.pt" ]; then
        download_file "$(get_url "models" "ner-det")" "$MODEL_DIR/ner-det.pt" "NER Det model"
    fi
    echo "[*] Models are ready."
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
    import_models
    ;;
5)
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
