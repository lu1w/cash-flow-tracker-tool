import os
from dotenv import load_dotenv

load_dotenv()


def get_bool_config(config_value: str):
    return config_value in ("true", "True", "1")


class AIConfig:
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    # An arbitrary string will do - connecting to locally running LLM doesn't need real authentication
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


class FileConfig:
    INPUT_DATA_DIR = os.getenv("INPUT_DATA_DIR", ".data/input")
    STANDARDIZED_DATA_DIR = os.getenv("STANDARDIZED_DATA_DIR", ".data/standardized")
    CATEGORIZED_DATA_DIR = os.getenv("CATEGORIZED_DATA_DIR", ".data/categorized")

    INPUT_PURCHASE_HISTORY_DATA_DIR = os.getenv("INPUT_PURCHASE_HISTORY_DATA_DIR", ".data/intput-purchase-history")

    OUTPUT_DATA_DIR = os.getenv("OUTPUT_DATA_DIR", ".data/output")
    OUTPUT_DATA_MONTHLY_DIR = os.getenv("OUTPUT_DATA_DIR", ".data/output") + "/monthly"
    OUTPUT_DATA_YEARLY_DIR = os.getenv("OUTPUT_DATA_DIR", ".data/output") + "/yearly"

    OUTPUT_SNAPSHOTS_DIR = os.getenv("OUTPUT_SNAPSHOTS_DIR", ".data/output-snapshots")

    CATEGORY_REFERENCE_DATA_DIR = os.getenv("CATEGORY_REFERENCE_DATA_DIR", ".data/category-reference")


class LoggerConfig:
    FILE_LOGGER_ENABLED = get_bool_config(os.getenv("FILE_LOGGER_ENABLED", "false"))  # useful when long logs
    FILE_LOGGER_FRESH_FILE_PER_RUN = get_bool_config(
        os.getenv("FILE_LOGGER_FRESH_FILE_PER_RUN", "false")
    )  # useful when comparing log files
    FILE_LOGGER_MODE = os.getenv("FILE_LOGGER_MODE", "w")[0]  # a=append, w=write


if __name__ == "__main__":
    print(f"OPENROUTER_API_KEY = {AIConfig.OPENROUTER_API_KEY}")
    print(f"OPENROUTER_BASE_URL = {AIConfig.OPENROUTER_BASE_URL}")
