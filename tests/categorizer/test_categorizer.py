"""
To run the test in this file:
    pytest tests/categorizer/test_categorizer.py
"""
import sys
import pandas as pd
import pytest
from pathlib import Path

from src.categorizer.categorizer import Categorizer, EMBEDDING_CATEGORY_RESOLVER
from src.config.config import FileConfig
from src.enum.column import Column
from src.utils.logger import test_log


@pytest.fixture
def data_file_standardized_data_no_category_csv() -> Path:
    # FIXME: this fixture's header uses "RAW Category" while src/enum/column.py defines
    # Column.CATEGORY_RAW.value as "Raw Category" (different casing) — stale since the
    # Column rename in commit ae6f566. Currently masked because no test reads that column
    # by name; regenerate the fixture to match Column.CATEGORY_RAW.
    return Path(f"{FileConfig.STANDARDIZED_DATA_DIR}/standardized_data_no_category.csv")


@pytest.fixture(scope="session")  # Created exactly once per test run. Shared globally across entire project.
def categorizer() -> Categorizer:
    categorizer = Categorizer()
    return categorizer


def test_categorize(categorizer: Categorizer, data_file_standardized_data_no_category_csv: pd.DataFrame):
    categorizer.categorize(data_file_standardized_data_no_category_csv)

    # Validate result
    input_df = pd.read_csv(data_file_standardized_data_no_category_csv)
    output_df = pd.read_csv(categorizer.get_output_csv_file_path(data_file_standardized_data_no_category_csv))

    assert len(input_df) == len(output_df)

    has_categorized_row = False

    # # Version 1
    # for (_, row) in output_df.iterrows():
    #     if not pd.isna(row[Column.CATEGORY]):
    #         print(f"type of category column : {type(row[Column.CATEGORY])}; boolean value {bool(row[Column.CATEGORY])}")
    #         has_categorized_row = True
    #         assert row[Column.CATEGORY_RESOLVER] == EMBEDDING_CATEGORY_RESOLVER

    # # Version 2
    # for row_tuple in output_df.itertuples(index=False):
    #     # Convert to a dictionary to keep bracket lookup clean and safe
    #     row = row_tuple._asdict()

    #     if not pd.isna(row[Column.CATEGORY]):
    #         print(f"type of category column : {type(row[Column.CATEGORY])}; boolean value {bool(row[Column.CATEGORY])}")
    #         has_categorized_row = True
    #         assert row[Column.CATEGORY_RESOLVER] == EMBEDDING_CATEGORY_RESOLVER

    # Version 3
    categorized_rows = output_df[output_df[Column.CATEGORY].notna()]
    assert not categorized_rows.empty
    assert (categorized_rows[Column.CATEGORY_RESOLVER.value] == EMBEDDING_CATEGORY_RESOLVER).all(), \
        "Some rows do not match the expected EMBEDDING_CATEGORY_RESOLVER"
