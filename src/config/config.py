import os
from dotenv import load_dotenv

load_dotenv()


def get_bool_config(config_value: str):
    return config_value in ("true", "True", "1")


class OpenRouterConfig:
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class FileConfig:
    INPUT_DATA_DIR = os.getenv("INPUT_DATA_DIR", ".data/input")
    STANDARDIZED_DATA_DIR = os.getenv("STANDARDIZED_DATA_DIR", ".data/standardized")
    CATEGORIZED_DATA_DIR = os.getenv("CATEGORIZED_DATA_DIR", ".data/categorized")
    OUTPUT_DATA_DIR = os.getenv("OUTPUT_DATA_DIR", ".data/output")
    OUTPUT_SNAPSHOTS_DIR = os.getenv("OUTPUT_SNAPSHOTS_DIR", ".data/output-snapshots")

    CATEGORY_REFERENCE_DATA_DIR = os.getenv("CATEGORY_REFERENCE_DATA_DIR", ".data/category-reference")


class LoggerConfig:
    FILE_LOGGER_ENABLED = get_bool_config(os.getenv("FILE_LOGGER_ENABLED", "false"))  # useful when long logs
    FILE_LOGGER_FRESH_FILE_PER_RUN = get_bool_config(
        os.getenv("FILE_LOGGER_FRESH_FILE_PER_RUN", "false")
    )  # useful when comparing log files
    FILE_LOGGER_MODE = os.getenv("FILE_LOGGER_MODE", "w")[0]  # a=append, w=write


if __name__ == "__main__":
    print(f"OPENROUTER_API_KEY = {OpenRouterConfig.OPENROUTER_API_KEY}")
    print(f"OPENROUTER_BASE_URL = {OpenRouterConfig.OPENROUTER_BASE_URL}")
