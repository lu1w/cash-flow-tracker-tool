"""
To run the test in this file:
    pytest tests/parse_strategy_tests/test_wechat_parse_strategy.py
"""
import pytest

from typing import List, Dict, Any
from src.models.input_model import WechatInputEntryModel
from src.models.transaction_entry_model import TransactionEntryModel
from src.parse_strategy.wechat_parse_strategy import WechatParseStrategy
from src.enum.account import Account
from src.enum.category_resolver import CategoryResolver


@pytest.mark.unit
def test_load_data__should_load_all_rows(data_file__wechat_input_data):
    data_models = WechatParseStrategy.load_data(data_file__wechat_input_data)
    assert len(data_models) == 11


@pytest.mark.unit
def test_parse_entry__should_parse_correct_field_values(data_models__alipay_input_data: List[WechatInputEntryModel]):
    for input_data_model in data_models__alipay_input_data:
        parsed_entry = WechatParseStrategy.parse_entry(input_data_model)

        assert parsed_entry.date == input_data_model.date_time
        assert len(parsed_entry.category_raw) > 0
        assert parsed_entry.category_resolver == CategoryResolver.RULES.value
        assert parsed_entry.account == Account.WECHAT.value
        assert parsed_entry.amount_absolute == abs(input_data_model.amount)
        assert parsed_entry.description == input_data_model.item_detail
