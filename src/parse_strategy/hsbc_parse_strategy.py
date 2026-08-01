import sys
import traceback
from enum import Enum
from pathlib import Path

import pandas as pd
from pandas import DataFrame, Series
from typing import List, Dict, Callable, override


# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.column import Column
from src.enum.currency import Currency
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, debug_log


class HsbcColumn(Enum):
    # Date,Description,Billing amount,Billing currency,Balance,Balance currency
    DATE = ("Date", True)
    ITEM_DETAIL = ("Description", True)
    NET_AMOUNT = ("Billing amount", True)
    CURRENCY = ("Billing currency", True)
    BALANCE = ("Balance", True)
    BALANCE_CURRENCY = ("Balance currency", True)

    def __init__(self, column_name: str, is_useful: bool):
        self.column_name = column_name
        self.is_useful = is_useful

    def get_unuseful_columns() -> List[str]:
        return [column.column_name for column in HsbcColumn if not column.is_useful]


class HsbcParseStrategy(ParseStrategyBase):
    # TODO: set this in a config so all accounts can be managed together
    account = Account.HSBC_HKD
    currency = Currency.HKD  # TODO: support multiple hsbc accounts with different current account, maybe needs to change to instance field
    file_extension = "csv"
    encoding = 'utf-8'

    # refund_category = "退款"
    cash_rebase_keyword = "CREDIT AS ADVISED"

    @classmethod
    def _get_category(cls, item_description: str) -> Category:
        if cls.cash_rebase_keyword in item_description:
            return CategoryInflow.CASH_REBATE.name
        return "TODO"

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> DataFrame:
        try:
            columns_to_drop = HsbcColumn.get_unuseful_columns()
            data = pd.read_csv(file_path, encoding=cls.encoding).drop(columns_to_drop, axis=1)
            return data
        except UnicodeDecodeError as e:
            logger.exception(f"Error in decoding the data file `{file_path}`: {e}")

    @override
    @classmethod
    def parse_row(cls, row: Series) -> Series:
        cashflow_direction = CashflowDirection.OUTFLOW if row[HsbcColumn.NET_AMOUNT.column_name][0] == "-" \
            else CashflowDirection.INFLOW
        net_amount = float(row[HsbcColumn.NET_AMOUNT.column_name].strip().replace(",", ""))

        # Populate output
        output_row: Series = Series([])

        # NOTE: if want to have up to seconds like `2026-03-06 00:00:00` in the output csv, convert the datetime to str.
        # HSBC does not have hh:mm:ss information, so all items will have `00:00:00`.
        date: pd.Timestamp = pd.to_datetime(row[HsbcColumn.DATE.column_name], format='%d/%m/%Y')
        output_row[Column.DATE.value] = date

        output_row[Column.CATEGORY.value] = cls._get_category(row[HsbcColumn.ITEM_DETAIL.column_name])
        output_row[Column.CATEGORY_RAW.value] = "--"

        output_row[Column.CURRENCY.value] = cls.currency.name
        output_row[Column.ACCOUNT.value] = cls.account.name

        output_row[Column.CASHFLOW_DIRECTION.value] = cashflow_direction.text
        output_row[Column.AMOUNT_ABSOLUTE.value] = abs(net_amount)
        output_row[Column.AMOUNT_NET.value] = net_amount

        output_row[Column.ACCOUNT_BALANCE.value] = float(row[HsbcColumn.BALANCE.column_name].strip().replace(",", ""))
        output_row[Column.DESCRIPTION.value] = row[HsbcColumn.ITEM_DETAIL.column_name]
        output_row[Column.REMARK.value] = ""  # manual edit

        output_row[Column.IS_AGGREGATED.value] = False
        # TODO: think about how to show the refund item
        output_row[Column.IS_REFUNDED.value] = "--"

        return output_row


if __name__ == "__main__":
    debug_log("Run from main.py to see the result")
