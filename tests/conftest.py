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


PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv(PROJECT_ROOT / ".env.test", override=True)

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


# @pytest.fixture
# def data_files_path(project_root: Path) -> Path:
#     path = project_root / "tests/fixtures"
#     return path

# @pytest.fixture
# def input_dir() -> Path:
#     return Path(os.getenv("INPUT_DATA_DIR"))


# @pytest.fixture
# def output_dir() -> Path:
#     return Path(os.getenv("OUTPUT_DATA_DIR"))


# @pytest.fixture
# def reference_dir() -> Path:
#     return Path(os.getenv("REFERENCE_DATA_DIR"))


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


if __name__ == "__main__":
    print()
    print(f"PROJECT_ROOT = {PROJECT_ROOT}")
