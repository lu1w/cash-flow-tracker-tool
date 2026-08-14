"""
To run this test:
    pytest tests/test_config.py
"""
from pathlib import Path

from src.config.config import FileConfig, OpenRouterConfig


def test_file_config_uses_test_env_paths(project_root: Path):
    assert FileConfig.INPUT_DATA_DIR == "tests/fixtures/input"
    assert FileConfig.STANDARDIZED_DATA_DIR == "tests/fixtures/standardized"
    assert FileConfig.OUTPUT_DATA_DIR == "tests/fixtures/output"
    assert FileConfig.OUTPUT_SNAPSHOTS_DIR == "tests/fixtures/output-snapshots"
    assert FileConfig.CATEGORY_REFERENCE_DATA_DIR == "tests/fixtures/category-reference"

    for path_value in (
        FileConfig.INPUT_DATA_DIR,
        FileConfig.STANDARDIZED_DATA_DIR,
        FileConfig.OUTPUT_DATA_DIR,
        FileConfig.OUTPUT_SNAPSHOTS_DIR,
        FileConfig.CATEGORY_REFERENCE_DATA_DIR,
    ):
        assert (project_root / path_value).exists()


def test_openrouter_config_uses_test_credentials():
    assert OpenRouterConfig.OPENROUTER_API_KEY == "test-key-not-used"
    assert OpenRouterConfig.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"
