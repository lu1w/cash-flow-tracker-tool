
import sys
import csv
from enum import Enum
from pathlib import Path

import pandas as pd
from pandas import DataFrame, Series
from typing import List, Dict, Callable, override, Any


# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.column import Column
from src.enum.currency import Currency
from src.enum.category_resolver import CategoryResolver
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.models.input_model import AlipayInputEntryModel
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, debug_log


class AlipayParseStrategy():
    """Parsing strategy for handling Alipay transaction history data."""

    account = Account.ALIPAY
    currency = Currency.CNY
    file_extension = "csv"
    encoding = 'gbk'

    # refund_category = "退款"

    num_skip_rows = 23

    @classmethod
    def load_data(cls, file_path: Path) -> List[Dict[str, Any]]:
        columns_to_drop = set(AlipayInputEntryModel.get_ignored_columns())

        try:
            data = cls._parse_csv(file_path, cls.encoding, columns_to_drop)
        except UnicodeDecodeError:
            # If the original encoding fails (e.g. GBK), fallback to utf-8
            cls.encoding = "utf-8"
            data = cls._parse_csv(file_path, cls.encoding, columns_to_drop)

        logger.info(f"Data (encoding={cls.encoding}) loaded successfully from file {file_path}")
        return data

    @classmethod
    def _parse_csv(cls, file_path: Path, encoding: str, columns_to_drop: set = set()) -> List[Dict[str, Any]]:
        with open(file_path, mode='r', encoding=encoding, newline='') as f:
            # Skip the required number of rows manually
            for _ in range(cls.num_skip_rows):
                next(f, None)

            # Parse the remaining rows into a dictionary and strip any leading/trailing whitespaces
            reader = csv.DictReader(f)
            if reader.fieldnames:
                reader.fieldnames = [field.strip() for field in reader.fieldnames]

            # Build the list of rows, skipping unuseful columns
            parsed_data = [
                {k: v for k, v in row.items() if k not in columns_to_drop}
                for row in reader
            ]
            return parsed_data

    # @classmethod
    # def parse(
    #     cls,
    #     row: Any,  # Your input row object / Pydantic model / dict
    #     cashflow_direction: Any,  # Your cashflow direction helper object
    #     derived_category: str,
    #     currency_name: str,
    #     account_value: str
    # ) -> Any:

    #     # Extract data using your original config safely
    #     raw_amount = float(row[AlipayColumn.AMOUNT.column_name])

    #     # Assuming cashflow_direction behaves like a multiplier when multiplying numeric types
    #     # (e.g. -1 for outbound, 1 for inbound)
    #     net_multiplier = int(cashflow_direction)

    #     return StandardizedRow(
    #         date=pd.to_datetime(row[AlipayColumn.DATE_TIME.column_name]).to_pydatetime(),
    #         category=derived_category,
    #         category_confidence=0.1,
    #         category_resolver=CategoryResolver.RULES.value,  # Extract the value/name from your Enum
    #         category_raw=str(row[AlipayColumn.CATEGORY.column_name]),
    #         currency=currency_name,
    #         account=account_value,
    #         cashflow_direction=cashflow_direction.text,
    #         amount_absolute=raw_amount,
    #         amount_net=net_multiplier * raw_amount,
    #         description=str(row[AlipayColumn.ITEM_DETAIL.column_name]),
    #         # Fields like account_balance, remark, is_aggregated, is_refunded
    #         # fallback onto the model's empty string defaults automatically!
    #     )
