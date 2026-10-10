"""
To run the test in this file:
    pytest tests/models_tests/test_input_model.py
"""
import csv
import pytest
from typing import List, Dict, Any

from src.models.input_model import AlipayInputEntryModel
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy
from src.utils.logger import debug_log


@pytest.mark.unit
def test_alipay_input_model_validate__should_succeed(data_file__alipay_input_data):
    data_rows = AlipayParseStrategy._load_data_rows(data_file__alipay_input_data)
    for row in data_rows:
        AlipayInputEntryModel.model_validate(row)
