"""
To run the test in this file:
    pytest tests/parse_strategy_tests/test_alipay_parse_strategy.py
"""
import pytest

from typing import List, Dict, Any
from src.models.input_model import AlipayInputEntryModel
from src.models.transaction_entry_model import TransactionEntryModel
from src.parse_strategy.alipay_parse_strategy import AlipayParseStrategy
from src.enum.account import Account
from src.enum.category_resolver import CategoryResolver


@pytest.mark.unit
def test_load_data__should_load_all_rows(data_file__alipay_input_data):
    data_models = AlipayParseStrategy.load_data(data_file__alipay_input_data)
    assert len(data_models) == 12


@pytest.mark.unit
def test_parse_entry__should_parse_correct_field_values(data_models__alipay_input_data: List[AlipayInputEntryModel]):
    for input_data_model in data_models__alipay_input_data:
        parsed_entry = AlipayParseStrategy.parse_entry(input_data_model)

        assert parsed_entry.date == input_data_model.date_time
        assert parsed_entry.category_raw == input_data_model.category
        assert parsed_entry.category_resolver == CategoryResolver.RULES.value
        assert parsed_entry.account == Account.ALIPAY.value
        assert parsed_entry.amount_absolute == abs(input_data_model.amount)
        assert parsed_entry.description == input_data_model.item_detail
