"""
conftest.py allows you to share fixtures, hooks, and plugins across multiple test files
without having to explicitly import them into each file.

Built-in Fixtures:
- The tmp_path fixture can provide a temporary directory unique to each test function.
- The monkeypatch fixture helps you to safely set/delete an attribute, dictionary item or
environment variable, or to modify sys.path for importing.
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent

# Force load the test environment BEFORE importing any local production code
test_env = PROJECT_ROOT / ".env.test"
print(f"Loading {test_env}...")
load_dotenv(test_env, override=True)

# After loading the test environment, it's safe of import production code
# without stopping pytest to override the env-vars
from src.config.config import FileConfig
from src.enum.account import Account
from src.models.input_model import AlipayInputEntryModel
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy


pytest_plugins = []
'''
e.g.
pytest_plugins = [
    "fixtures.standardized.standardized_data_fixtures",
    "fixtures.output.output_data_fixtures",
]
'''


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture  # TODO: can remove this
def temp_input_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "input"
    path.mkdir()
    monkeypatch.setenv("INPUT_DATA_DIR", str(path))
    return path


@pytest.fixture  # TODO: can remove this
def temp_output_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "output"
    path.mkdir()
    monkeypatch.setenv("OUTPUT_DATA_DIR", str(path))
    return path


# Data File Fixtures - Helper


def _load_alipay_input_data_models(file_path: Path) -> List[AlipayInputEntryModel]:
    return AlipayParseStrategy.load_data_models(file_path)


@pytest.fixture(scope="session")
def test_account() -> Account:
    return Account.CASH_HKD


# Data File Fixtures - Input

@pytest.fixture(scope="session")
def data_file__alipay_input_data() -> Path:
    return Path(f"{FileConfig.INPUT_DATA_DIR}/alipay/alipay_input_data.csv")


@pytest.fixture(scope="session")
def data_models__alipay_input_data(data_file__alipay_input_data) -> List[AlipayInputEntryModel]:
    return _load_alipay_input_data_models(data_file__alipay_input_data)


# Data File Fixtures - Standardized


@pytest.fixture(scope="session")
def data_file__standardized_data_no_category_csv(test_account) -> Path:
    return Path(f"{FileConfig.STANDARDIZED_DATA_DIR}/{test_account.dir_name}/standardized_data_no_category.csv")


# Data File Fixtures - Output

@pytest.fixture(scope="session")
def data_file__monthly_output_data_csv() -> Path:
    return Path(f"{FileConfig.OUTPUT_MONTHLY_DATA_DIR}/output_data.csv")


if __name__ == "__main__":
    print()
    print(f"PROJECT_ROOT = {PROJECT_ROOT}")
