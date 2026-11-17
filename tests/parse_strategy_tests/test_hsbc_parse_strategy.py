"""
To run the test in this file:
    pytest tests/parse_strategy_tests/test_hsbc_parse_strategy.py
"""
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category import CategoryInflow, CategoryOutflow
from src.enum.category_resolver import CategoryResolver
from src.enum.currency import Currency
from src.parse_strategy.hsbc_parse_strategy import HsbcParseStrategy


@pytest.fixture
def data_file__hsbc_input_data(tmp_path: Path) -> Path:
    file_path = tmp_path / "hsbc_input_data.csv"
    file_path.write_text(
        "\n".join([
            "Date,Description,Billing amount,Billing currency,Balance,Balance currency",
            '06/03/2026,CREDIT AS ADVISED,"1,200.00",HKD,"10,000.50",HKD',
            '06/03/2026,SOME MERCHANT,"-45.60",HKD,"9,954.90",HKD',
        ]),
        encoding="utf-8",
    )
    return file_path


@pytest.mark.unit
def test_load_data__should_load_all_rows(data_file__hsbc_input_data: Path):
    data_models = HsbcParseStrategy.load_data(data_file__hsbc_input_data)
    assert len(data_models) == 2
    assert data_models[0].net_amount == Decimal("1200.00")
    assert data_models[1].net_amount == Decimal("-45.60")
    assert data_models[0].date.isoformat() == "2026-03-06"


@pytest.mark.unit
def test_parse_entry__should_parse_correct_field_values(data_file__hsbc_input_data: Path):
    rebate, purchase = HsbcParseStrategy.load_data(data_file__hsbc_input_data)

    parsed_rebate = HsbcParseStrategy.parse_entry(rebate)
    assert parsed_rebate.date == datetime(2026, 3, 6)
    assert parsed_rebate.category == CategoryInflow.CASH_REBATE.value
    assert parsed_rebate.category_raw == ""
    assert parsed_rebate.category_resolver == CategoryResolver.RULES.value
    assert parsed_rebate.category_confidence == 0.1
    assert parsed_rebate.account == Account.HSBC_HKD.value
    assert parsed_rebate.currency == Currency.HKD.value
    assert parsed_rebate.cashflow_direction == CashflowDirection.INFLOW.display_name
    assert parsed_rebate.amount_absolute == Decimal("1200.00")
    assert parsed_rebate.amount_net == Decimal("1200.00")
    assert parsed_rebate.account_balance == Decimal("10000.50")
    assert parsed_rebate.description == "CREDIT AS ADVISED"
    assert parsed_rebate.is_aggregated is False
    assert parsed_rebate.refunded is False

    parsed_purchase = HsbcParseStrategy.parse_entry(purchase)
    assert parsed_purchase.category == CategoryOutflow.UNKNOWN.value
    assert parsed_purchase.cashflow_direction == CashflowDirection.OUTFLOW.display_name
    assert parsed_purchase.amount_absolute == Decimal("45.60")
    assert parsed_purchase.amount_net == Decimal("-45.60")
    assert parsed_purchase.account_balance == Decimal("9954.90")
    assert parsed_purchase.description == "SOME MERCHANT"
