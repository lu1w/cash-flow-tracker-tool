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
    entries = HsbcParseStrategy.load_data(data_file__hsbc_input_data)

    rebate = HsbcParseStrategy.parse_entry(entries[0])
    assert rebate.date == datetime(2026, 3, 6)
    assert rebate.category == CategoryInflow.CASH_REBATE.value
    assert rebate.category_by_rules == rebate.category
    assert not rebate.category_by_categorizer
    assert not rebate.category_by_human
    assert rebate.category_raw == "CREDIT AS ADVISED"
    assert rebate.account == Account.HSBC_HKD.value
    assert rebate.currency == Currency.HKD.value
    assert rebate.cashflow_direction == CashflowDirection.INFLOW.display_name
    assert rebate.amount_absolute == Decimal("1200.00")
    assert rebate.amount_net == Decimal("1200.00")
    assert rebate.account_balance == Decimal("10000.50")
    assert rebate.description == "CREDIT AS ADVISED"
    assert rebate.is_aggregated is False
    assert rebate.refunded is False

    purchase = HsbcParseStrategy.parse_entry(entries[1])
    assert purchase.category == CategoryOutflow.UNKNOWN.value
    assert purchase.category_by_rules == purchase.category
    assert not purchase.category_by_categorizer
    assert not purchase.category_by_human
    assert purchase.cashflow_direction == CashflowDirection.OUTFLOW.display_name
    assert purchase.amount_absolute == Decimal("45.60")
    assert purchase.amount_net == Decimal("-45.60")
    assert purchase.account_balance == Decimal("9954.90")
    assert purchase.description == "SOME MERCHANT"
