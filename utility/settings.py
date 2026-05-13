import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple, Type

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class JsonConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A custom settings source that loads variables from a JSON file.
    """

    def __call__(self) -> dict[str, Any]:
        config_path = Path(
            os.environ.get("NLA_CONFIG_FILE", "configs/configurations.json")
        )
        if config_path.exists():
            return json.loads(config_path.read_text())
        else:
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

    def get_field_value(self, field: Any, field_name: str) -> Tuple[Any, str, bool]:
        # Required by abstract base class in newer pydantic-settings,
        # but unused because we override __call__
        return None, field_name, False

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        # Required by abstract base class in newer pydantic-settings,
        # but unused because we override __call__
        return value


class ElasticSettings(BaseSettings):
    username: str = "elastic"
    password: str = ""
    base_url: str = "https://localhost:9200"
    index_name_gnd: str = "gnd_lobid"
    index_name_wikidata: str = "wikidata"

    model_config = SettingsConfigDict(
        env_prefix="ELASTIC_",
        env_file=(
            ".env_template",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    # Dynamic Runtime Variables
    JOB_ID: str = "chnobli"
    PATH_TO_GROUND_TRUTH: str | None = None
    CUSTOM_PATHS: list[str] | None = None
    CUSTOM_TAG_PATH: str | None = None
    EVAL_TOPK: int | None = None
    INKB_SCORE: str | None = None
    USE_RICH_LOGGING: bool = True

    # JSON Config Fields (configs/configurations.json)
    PATH_TO_INPUT_FOLDERS: str = "./data/input/"
    PATH_TO_NER_MODEL_1: str = "./models/ner-bio.pt"
    PATH_TO_NER_MODEL_2: str = "./models/ner-det.pt"
    PATH_TO_OUTFILE_FOLDER: str = "./data/output/"
    PATH_TO_ABBREVIATION_FILE: str = "./src/preprocessing/abbrevs.txt"
    PATH_TO_GROUND_TRUTH_FUZZY: str = (
        "./data/ground_truth/ground_truth_linked/with_fuzzy_matching/"
    )
    PATH_TO_GROUND_TRUTH_NOTFUZZY: str = (
        "./data/ground_truth/ground_truth_linked/without_fuzzy_matching/"
    )
    DATA2_MNT: str = "./adl/"
    VD_API_TOKEN: str = "./src/.env.api.token"
    VD_MAX_RETRIES: int = 100
    VD_QUERY_CHUNK_LEN: int = 5000
    VD_MAX_DIST: float = 0.6
    VD_CONTEXT_WINDOW_LEN: int = 30
    SENTENCE_BATCH_SIZE: int = 128
    GND_LIMIT: int = 15
    WIKIDATA_LIMIT: int = 5
    LINKED_PERSONS_LIMIT: int = 10
    BATCH_SIZE: int = 4

    # Env Variables (.env_template / .env)
    PATH_TO_CA_CERT: str = "../secrets/certs/ca/ca.crt"

    # Embedding Service
    CLIENT_ID: str | None = None
    CLIENT_SECRET: str | None = None
    EMBEDDINGS_ENDPOINT: str | None = None
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: str = "19530"

    # Configure Pydantic to read from env files
    model_config = SettingsConfigDict(
        env_file=(
            ".env_template",
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True,
    )

    # Elastic Search settings in a separate container
    es: ElasticSettings = ElasticSettings()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Priority (highest to lowest):
        # 1. Environment variables (env_settings)
        # 2. .env files (dotenv_settings)
        # 3. JSON File (configs/configurations.json)
        # 4. Defaults in class
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
        )


# Global settings instance
settings = Settings()

if __name__ == "__main__":
    print("Main settings:")
    dump_dict = settings.model_dump(exclude={"es"})
    print(json.dumps(dump_dict, indent=2))

    print("\nElastic Settings:")
    print(settings.es.model_dump_json(indent=2))
