"""
To run the test in this file:
    pytest tests/categorizer_tests/test_categorizer.py
"""
import pandas as pd
import pytest
from pathlib import Path

from src.categorizer.categorizer import Categorizer
from src.enum.account import Account
from src.enum.category_resolver import CategoryResolver
from src.config.config import FileConfig
from src.enum.column import Column
from src.utils.logger import debug_log


@pytest.fixture(scope="session")  # Created exactly once per test run. Shared globally across entire project.
def categorizer() -> Categorizer:
    categorizer = Categorizer()
    return categorizer


@pytest.mark.unit
def test__map_standardized_file_to_categorized_file(
    categorizer: Categorizer,
    data_file__standardized_data_no_category_csv: Path
):
    result = categorizer._map_standardized_file_to_categorized_file(data_file__standardized_data_no_category_csv)
    assert str(result).endswith(data_file__standardized_data_no_category_csv.name)


@pytest.mark.integration
def test_process_all_standardized_files(
        categorizer: Categorizer,
        test_account,
        data_file__standardized_data_no_category_csv: Path):
    categorizer.process_all_standardized_files(accounts=(test_account,))

    # Validate result
    input_df = pd.read_csv(data_file__standardized_data_no_category_csv)
    output_df = pd.read_csv(categorizer._map_standardized_file_to_categorized_file(
        data_file__standardized_data_no_category_csv))

    assert len(input_df) == len(output_df)

    categorized_rows = output_df[output_df[Column.CATEGORY].notna()]
    assert not categorized_rows.empty
    assert (categorized_rows[Column.CATEGORY_RESOLVER.value] == CategoryResolver.EMBEDDING).all(), \
        "Some rows do not match the expected CategoryResolver.EMBEDDING"
