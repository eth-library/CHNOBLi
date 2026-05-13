# CHNOBLi

**A named entity linking pipeline for retro-digitized documents**

[![eth-library - CHNOBLi](https://img.shields.io/static/v1?label=eth-library&message=CHNOBLi&color=blue&logo=github)](https://github.com/eth-library/CHNOBLi "Go to GitHub repo")
[![GitHub stars](https://img.shields.io/github/stars/eth-library/CHNOBLi?style=social)](https://github.com/eth-library/CHNOBLi)
[![GitHub forks](https://img.shields.io/github/forks/eth-library/CHNOBLi?style=social)](https://github.com/eth-library/CHNOBLi)
[![GitHub tag](https://img.shields.io/github/tag/eth-library/CHNOBLi?include_prereleases=&sort=semver&color=blue)](https://github.com/eth-library/CHNOBLi/releases/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)
[![Issues](https://img.shields.io/github/issues/eth-library/CHNOBLi)](https://github.com/eth-library/CHNOBLi/issues)

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Local Setup](#local-setup)
  - [Docker](#docker)
- [Using Your Data](#using-your-data)
- [Resources](#resources)
- [License](#license)

## Overview

CHNOBLi is a pipeline for named entity linking and disambiguation in retro-digitized documents. It processes text through three main stages:

| Component | Purpose |
|-----------|---------|
| **Tagging** | Extract and tag named entities from OCR text using pre-trained NER models |
| **Aggregation** | Combine and normalize entity mentions across documents and sources |
| **Linking** | Link mentions to knowledge bases (Wikipedia, Wikidata, GND) and resolve identity |

## Installation

### Installation

The easiest way to set up the project is using the interactive setup wizard:

```bash
git clone git@github.com:eth-library/CHNOBLi.git
cd CHNOBLi
make setup
```

The wizard will guide you through:
1. Creating your `.env` configuration file.
2. Choosing between **Minimal Setup** (using remote APIs) or **Full Local Setup** (cloning and setting up local databases).

Once the databases are running, you can import the required data using:

```bash
make import-data
```

### Manual Setup (Optional)

If you prefer to set everything up manually, follow these steps:

#### Step 1: Clone Repository

```bash
git clone git@github.com:eth-library/CHNOBLi.git
cd CHNOBLi
```

#### Step 2: Create Environment

**Option A: Using Conda**
```bash
conda create -n env_chnobli python=3.12 ipython
conda activate env_chnobli
```

**Option B: Using venv**
```bash
python3.12 -m venv .env_chnobli # Windows: py -3.12 -m venv .env_chnobli
source .env_chnobli/bin/activate  # Windows: .env_chnobli\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Download Models

Download the tagging models from [here](https://www.research-collection.ethz.ch/bitstreams/5be21deb-f852-4317-b428-162326e2a741/download) and [here](https://www.research-collection.ethz.ch/bitstreams/370809dd-190b-4687-87e6-73e42367dee1/download) and save them to the `models/` directory.

#### Step 5: Configure ElasticSearch

A public API endpoint is coming soon. To set up your own:

1. Follow the setup guide in [CHNOBLi-elasticsearch](https://github.com/eth-library/CHNOBLi-elasticsearch)
2. Update `CHNOBLi/.env_template` with your endpoints and index names
3. Rename file to `.env`
4. Copy the certificate hierarchy: `secrets/certs/ca/ca.crt`

#### Step 6: Configure Milvus

A public API endpoint is coming soon. To set up your own:

1. Set up Milvus following the setup guide in [CHNOBLi-vectordb](https://github.com/eth-library/CHNOBLi-vectordb)
2. Update `CHNOBLi/.env_template` with your host and port
3. Rename file to `.env`

### 4. Management with Makefile

The project includes a `Makefile` to simplify common tasks and ensure consistent environments (especially regarding file permissions).

#### Setup & Data
- **`make setup`**: Run the interactive configuration wizard.
- **`make import-data`**: Interactive tool to download and import Wikidata, GND, and Milvus data.

#### Container Management
- **`make build`**: Build the Docker images from source.
- **`make up`**: Start the linking pipeline in the background.
- **`make down`**: Stop and remove all containers.
- **`make logs`**: Tail the logs from all running services.

#### Interactive Access
- **`make shell`**: Drop into a bash shell inside the `linking` container.
- **`make shell-root`**: Same as above, but with root privileges.

### Docker

Run

```docker compose --file docker-compose-dev.yml up```

that automatically sets up your environment for you, although you still need to set up your own vector database and ElasticSearch index. To link you can then call

```docker exec -it linking sh scripts/link_example.sh```

## Quick Start

### Try It with Example Data

**1. Tag example documents**
```bash
sh scripts/tag_example.sh
```
Output: `data/output/tag/`

**2. Link entities**
```bash
sh scripts/link_example.sh
```
Output: `data/output/link/`

**3. Evaluate results**
```bash
sh scripts/eval_example.sh
```
Output: `data/output/eval_ref.json`

## Using Your Data

### Input Format: OCR Data

The tagging component expects word coordinates (as from ABBYY FineReader). If your OCR comes from another source, we provide transformation utilities:

**Transkribus**
```python
from utility.utils import transkribus_xml_to_approx_word_coord
```

**E-Rara**
```python
from utility.utils import erara_xml_to_word_coord
```

**Tesseract or Plain Text**
```python
from utility.utils import txt_file_to_word_coord
```

> **Contributing:** Have a transformation function for another format? Please submit a pull request!

Once it is transformed, you can run the pipeline just as you did with the example data.

### Custom Tagging Output

#### Transformation

If you already have entity extractions (e.g., from SpaCy), transform them to our format:

**Input example:**
```json
{
   "mention": "Kamal Kharrazi",
   "offset": 237,
   "length": 14,
   "docName": "APW19981109_0464.htm"
}
```

**Transform using:**
```python
from utility.utils import offset_len_to_linking_input
```

This produces output like:
```json
{
   "info": {
      "lastnames": ["Kharrazi"],
      "firstnames": ["Kamal"],
      "abbr_firstnames": [],
      "address": [],
      "titles": [],
      "occupations": [],
      "others": [],
      "type": "PER",
      "id": 0,
      "gt_wikipedia": "Kamal_Kharazi",
      "gt_wikidata": "Q435799",
      "gt_gnd": "1222390949"
   },
   "pageNo": 0,
   "pageNames": "APW19981109_0464.htm",
   "pid": "APW19981109_0464.htm",
   "sentenceNo": 0,
   "positions": "237:14",
   "articles": "",
   "context": "al bodies about the U.S.-funded  Radio Free Europe  , the Iran Daily reported Monday. \n\n It quoted  Foreign Minister    Kamal Kharrazi   as saying the radio "was set up to interfere in Iran\'s internal affairs.\'\' \n\n It did not say when the complaints wil"
}
```

#### Linking

**1. Configure your data path**

Edit `configs/configurations_customtag.json` and set `CUSTOM_TAGGING_OUTPUT` to your data path.

**2. Run aggregation (with linking)**
```bash
python main.py --tasks finish --config_file configs/configurations_customtag.json
```

**Or skip aggregation and only link:**
```bash
python main.py --tasks link --config_file configs/configurations_customtag.json
```

> **Note on context:** The pipeline reads context from ABBYY FineReader format, which is why for your custom data, you have to include this `"context"` key with the context string explicitly. If your data doesn't include context, simply omit the `"context"` key and the disambiguation via vector database will be skipped.

> **Note on dates:** The publication year is used for sanity checks (e.g., not considering people born after that year). For custom data, this defaults to year 3000 — adjust as needed in `main.py`.

## Resources

### Ground-Truth Data

Download training and evaluation datasets from [Hugging Face](https://huggingface.co/datasets/rashiti-g/eperiodica-chnobli):

- Annotated entity mentions
- Linked entities with Wikipedia/Wikidata/GND IDs
- Retro-digitized documents

## Citation

**Citation format coming soon...**

## License

Released under [MIT](/LICENSE) by [@eth-library](https://github.com/eth-library).