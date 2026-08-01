import os
from dotenv import load_dotenv

load_dotenv()


class OpenRouterConfig:
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class FileConfig:
    INPUT_DATA_DIR = os.getenv("INPUT_DATA_DIR", ".data/input")
    STANDARDIZED_DATA_DIR = os.getenv("STANDARDIZED_DATA_DIR", ".data/standardized")
    CATEGORIZED_DATA_DIR = os.getenv("CATEGORIZED_DATA_DIR", ".data/categorized")
    OUTPUT_DATA_DIR = os.getenv("OUTPUT_DATA_DIR", ".data/output")
    OUTPUT_SNAPSHOTS_DIR = os.getenv("OUTPUT_SNAPSHOTS_DIR", ".data/output-snapshots")

    REFERENCE_DATA_DIR = os.getenv("REFERENCE_DATA_DIR", ".data/reference")


if __name__ == "__main__":
    print(f"OPENROUTER_API_KEY = {OpenRouterConfig.OPENROUTER_API_KEY}")
    print(f"OPENROUTER_BASE_URL = {OpenRouterConfig.OPENROUTER_BASE_URL}")
