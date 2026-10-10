"""
To run the test in this file:
    pytest tests/models_tests/test_transaction_entry_model.py
"""
import csv
import pytest

from src.models.transaction_entry_model import TransactionEntryModel
from src.utils.logger import debug_log


@pytest.mark.unit
def test_model_validate__should_succeed(data_file__monthly_output_data_csv):
    with open(data_file__monthly_output_data_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            TransactionEntryModel.model_validate(row)
