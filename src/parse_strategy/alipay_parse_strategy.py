
import sys
from enum import Enum
from pathlib import Path

import pandas as pd
from pandas import DataFrame, Series
from typing import List, Dict, Callable


# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.column import Column
from src.enum.currency import Currency
from src.enum.category import CategoryInflow, CategoryOutflow
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger


class AlipayColumn(Enum):
    # 交易时间,交易分类,交易对方,对方账号,商品说明,收/支,金额,收/付款方式,交易状态,交易订单号,商家订单号,备注,
    DATE_TIME = ("交易时间", True)
    CATEGORY = ("交易分类", True)
    COUNTERPARTY = ("交易对方", True)
    COUNTERPARTY_ACCOUNT = ("对方账号", False)
    ITEM_DETAIL = ("商品说明", True)
    CASHFLOW_DIRECTION = ("收/支", True)
    AMOUNT = ("金额", True)
    PAYMENT_METHOD = ("收/付款方式", False)
    TRANSACTION_STATUS = ("交易状态", False)
    TRANSACTION_NUMBER = ("交易订单号", False)
    VENDOR_ORDER_NUMBER = ("商家订单号", False)
    REMARK = ("备注", False)

    def __init__(self, column_name: str, is_useful: bool):
        self.column_name = column_name
        self.is_useful = is_useful

    def get_unuseful_columns() -> List[str]:
        return [column.column_name for column in AlipayColumn if not column.is_useful]


ALIPAY_CASHFLOW_DIRECTION: Dict[str, CashflowDirection] = {
    "收入": CashflowDirection.INFLOW,
    "支出": CashflowDirection.OUTFLOW,
    "不计收支": CashflowDirection.UNKNOWN  # TODO: check why does this show up in the data
}

ALIPAY_INFLOW_CATEGORY_MAPPING: Dict[str, Callable[[Series], CategoryInflow]] = {
    "退款": lambda _: CategoryInflow.REFUND.name,
    "转账红包": lambda s: CategoryInflow.TRANSACTION.name if s[AlipayColumn.ITEM_DETAIL.column_name] == "转账" else CategoryInflow.GIFT.name
}

# TODO: implementation of the non-deterministic mapping functions
ALIPAY_OUTFLOW_CATEGORY_MAPPING: Dict[str, Callable[[Series | None], CategoryOutflow]] = {
    "交通出行": lambda _: CategoryOutflow.TRANSPORTATION.name,
    "日用百货": lambda _: CategoryOutflow.DAILY_NECESSITY.name,
    "家居家装": lambda _: CategoryOutflow.DAILY_NECESSITY.name,
    "酒店旅游": lambda _: CategoryOutflow.HOUSING.name,
    "运动户外": lambda _: CategoryOutflow.FITNESS.name,
    "服饰装扮": lambda _: CategoryOutflow.CLOTHING.name,
    "美容美发": lambda _: CategoryOutflow.BEAUTY.name,
    "医疗健康": lambda _: CategoryOutflow.UNKNOWN.name,
    "文化休闲": lambda _: CategoryOutflow.UNKNOWN.name,
    "商业服务": lambda _: CategoryOutflow.UNKNOWN.name,
    "其他": lambda _: CategoryOutflow.UNKNOWN.name,
}


class AlipayParseStrategy(ParseStrategyBase):
    account = Account.ALIPAY
    currency = Currency.CNY
    file_extension = "csv"
    encoding = 'gbk'

    refund_category = "退款"

    @classmethod
    def load_data(cls, file_path: Path) -> DataFrame:
        logger.info(f"Start loading data for file {file_path}")

        try:
            columns_to_drop = AlipayColumn.get_unuseful_columns()
            try:
                data = pd.read_csv(
                    # GBK is a more comprehensive superset of the GB2312 standard,
                    # and it is often more compatible with a wider range of simplified Chinese characters
                    # you might encounter in modern files. If one encoding doesn't work, try the other.
                    file_path, skiprows=24, encoding=cls.encoding
                ).drop(columns_to_drop, axis=1)
            except UnicodeDecodeError:
                # If not gbk, use utf-8
                cls.encoding = "utf-8"
                data = pd.read_csv(file_path, skiprows=24, encoding=cls.encoding).drop(columns_to_drop, axis=1)

            logger.info(f"Data (encoding={cls.encoding}) loaded successfull from file {file_path}.")

            return data

        except Exception as e:
            logger.error(
                f"Error loading CSV ({file_path}): {e}")

    @classmethod
    def parse_row(cls, row: Series) -> Series:
        # output_data: Dict[str, str] = {}
        cashflow_direction = ALIPAY_CASHFLOW_DIRECTION[row[AlipayColumn.CASHFLOW_DIRECTION.column_name]]

        output_row: Series = Series([])

        output_row[Column.DATE.value] = row[AlipayColumn.DATE_TIME.column_name]

        output_row[Column.CATEGORY.value] = \
            ALIPAY_INFLOW_CATEGORY_MAPPING[row[AlipayColumn.CATEGORY.column_name]](row) if cashflow_direction == CashflowDirection.INFLOW \
            else ALIPAY_OUTFLOW_CATEGORY_MAPPING[row[AlipayColumn.CATEGORY.column_name]](row) if cashflow_direction == CashflowDirection.OUTFLOW \
            else row[AlipayColumn.CATEGORY.column_name]
        output_row[Column.CATEGORY_RAW.value] = row[AlipayColumn.CATEGORY.column_name]

        output_row[Column.CURRENCY.value] = cls.currency.name
        output_row[Column.ACCOUNT.value] = cls.account.name

        output_row[Column.CASHFLOW_DIRECTION.value] = cashflow_direction.text
        output_row[Column.AMOUNT_ABSOLUTE.value] = row[AlipayColumn.AMOUNT.column_name]
        output_row[Column.AMOUNT_NET.value] = cashflow_direction * row[AlipayColumn.AMOUNT.column_name]

        output_row[Column.ACCOUNT_BALANCE.value] = "todo"
        output_row[Column.DETAILS.value] = row[AlipayColumn.ITEM_DETAIL.column_name]
        output_row[Column.REMARK.value] = "--"

        # TODO: handle aggregation; if aggregated, should have recored split to single items,
        # and the aggregated record should not be recorded in analysis
        output_row[Column.IS_AGGREGATED.value] = "todo"
        # TODO: think about how to show the refund item
        output_row[Column.IS_REFUND.value] = row[AlipayColumn.CATEGORY.column_name] == cls.refund_category

        return output_row

    @classmethod
    def fetch_input_file_date(cls, input_file_path: str) -> str:
        # `.data/alipay/支付宝交易明细(20251215-20260315).csv` -> `(20251215-20260315)`
        return str(input_file_path).split('/')[-1][7:26]  # TODO: handle different separator for different OS


if __name__ == "__main__":
    # from pprint import pprint
    # pprint(AlipayParseStrategy.__dict__)

    AlipayParseStrategy.execute()
