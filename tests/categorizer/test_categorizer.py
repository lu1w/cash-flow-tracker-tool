"""
To run the test in this file:
    pytest tests/categorizer/test_categorizer.py
"""
import pandas as pd
import pytest
from pathlib import Path

from src.categorizer.categorizer import Categorizer, EMBEDDING_CATEGORY_RESOLVER
from src.config.config import FileConfig
from src.enum.column import Column
from src.utils.logger import debug_log


@pytest.fixture
def data_file_standardized_data_no_category_csv() -> Path:
    return Path(f"{FileConfig.STANDARDIZED_DATA_DIR}/account0/standardized_data_no_category.csv")


@pytest.fixture(scope="session")  # Created exactly once per test run. Shared globally across entire project.
def categorizer() -> Categorizer:
    categorizer = Categorizer()
    return categorizer


def test_get_output_csv_file_path(categorizer: Categorizer):
    result = categorizer.get_output_csv_file_path((Path("account0/test.csv")))
    assert str(result).endswith("account0/test.csv")


def test_categorize(categorizer: Categorizer, data_file_standardized_data_no_category_csv: pd.DataFrame):
    categorizer.categorize(data_file_standardized_data_no_category_csv)

    # Validate result
    input_df = pd.read_csv(data_file_standardized_data_no_category_csv)
    output_df = pd.read_csv(categorizer.get_output_csv_file_path(data_file_standardized_data_no_category_csv))

    assert len(input_df) == len(output_df)

    categorized_rows = output_df[output_df[Column.CATEGORY].notna()]
    assert not categorized_rows.empty
    assert (categorized_rows[Column.CATEGORY_RESOLVER.value] == EMBEDDING_CATEGORY_RESOLVER).all(), \
        "Some rows do not match the expected EMBEDDING_CATEGORY_RESOLVER"
