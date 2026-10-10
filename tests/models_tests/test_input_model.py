"""
To run the test in this file:
    pytest tests/models_tests/test_input_model.py
"""
import csv
import pytest
from typing import List, Dict, Any
from pathlib import Path

from src.config.config import FileConfig
from src.models.input_model import AlipayInputEntryModel
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy
from src.utils.logger import debug_log


@pytest.fixture
def data_file__alipay_input_data() -> Path:
    return Path(f"{FileConfig.INPUT_DATA_DIR}/alipay/alipay_input_data.csv")


@pytest.fixture
def data__alipay_input_data(data_file_alipay_input_data) -> List[Dict[str, Any]]:
    return _read_alipay_data(data_file_alipay_input_data)


def _read_alipay_data(file_path: Path) -> List[Dict[str, Any]]:
    return AlipayParseStrategy.load_data(file_path)


def test_alipay_input_model_validate(data_alipay_input_data):
    for row in data_alipay_input_data:
        debug_log(row)
