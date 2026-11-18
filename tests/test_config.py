"""
To run this test:
    pytest tests/test_config.py

The test is asserting on the settings in `.env.test` file.
"""
from pathlib import Path

from src.config.config import FileConfig, OpenRouterConfig

# TODO(PL8): clean up the test directory


def test_file_config_uses_test_env_paths(project_root: Path):
    assert FileConfig.INPUT_DATA_DIR == "tests/.test_data/inputs/input"
    assert FileConfig.STANDARDIZED_DATA_DIR == "tests/.test_data/inputs/standardized"
    # assert FileConfig.OUTPUT_DATA_DIR == "tests/.test_data/output"
    assert FileConfig.OUTPUT_MONTHLY_DATA_DIR == "tests/.test_data/inputs/output/monthly"
    assert FileConfig.OUTPUT_SNAPSHOTS_DIR == "tests/.test_data/inputs/output-snapshots"
    assert FileConfig.CATEGORY_REFERENCE_DATA_DIR == "tests/.test_data/inputs/category-reference"

    for path_value in (
        FileConfig.INPUT_DATA_DIR,
        FileConfig.STANDARDIZED_DATA_DIR,
        FileConfig.OUTPUT_MONTHLY_DATA_DIR,
        FileConfig.OUTPUT_SNAPSHOTS_DIR,
        FileConfig.CATEGORY_REFERENCE_DATA_DIR,
    ):
        assert (project_root / path_value).exists()


def test_openrouter_config_uses_test_credentials():
    assert OpenRouterConfig.OPENROUTER_API_KEY == "test-key-not-used"
    assert OpenRouterConfig.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"
