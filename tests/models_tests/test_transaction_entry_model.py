"""
To run the test in this file:
    pytest tests/models_tests/test_transaction_entry_model.py
"""
import csv
import pytest
from pathlib import Path

from src.config.config import FileConfig
from src.models.transaction_entry_model import TransactionEntryModel
from src.utils.logger import debug_log


@pytest.fixture
def data_file_monthly_output_data_csv() -> Path:
    return Path(f"{FileConfig.OUTPUT_DATA_MONTHLY_DIR}/output_data.csv")


def test_model_validate(data_file_monthly_output_data_csv):
    with open(data_file_monthly_output_data_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            debug_log(row)
            TransactionEntryModel.model_validate(row)
        # entry = [OutputTransactionEntryModel.model_validate(row) for row in reader]
