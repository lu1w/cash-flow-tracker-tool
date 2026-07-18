
import sys
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
from src.utils.logger import logger, test_log


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
    "转账红包": lambda row: CategoryInflow.TRANSACTION.name if row[AlipayColumn.ITEM_DETAIL.column_name] == "转账" else CategoryInflow.GIFT.name
}

# TODO: implementation of the non-deterministic mapping functions
ALIPAY_OUTFLOW_CATEGORY_MAPPING: Dict[str, Callable[[Series | None], CategoryOutflow]] = {
    "交通出行": lambda _: CategoryOutflow.TRANSPORTATION.name,
    "日用百货": lambda _: CategoryOutflow.LIVING.name,
    "家居家装": lambda _: CategoryOutflow.LIVING.name,
    "生活服务": lambda _: CategoryOutflow.LIVING.name,
    "餐饮美食": lambda _: CategoryOutflow.FOOD.name,
    "酒店旅游": lambda _: CategoryOutflow.HOUSING.name,
    "教育培训": lambda _: CategoryOutflow.EDUCATION.name,
    "运动户外": lambda _: CategoryOutflow.FITNESS.name,
    "服饰装扮": lambda _: CategoryOutflow.CLOTHING.name,
    "美容美发": lambda _: CategoryOutflow.BEAUTY.name,
    "数码电器": lambda _: CategoryOutflow.ELECTRONICS.name,
    "充值缴费": lambda row: CategoryOutflow.TELECOMMUNICATION.name if row[AlipayColumn.COUNTERPARTY.column_name] == "中国移动" else CategoryOutflow.UNKNOWN.name,
    "住房物业": lambda _: CategoryOutflow.UNKNOWN.name,
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

    # refund_category = "退款"

    num_skip_rows = 23

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> DataFrame:
        columns_to_drop = AlipayColumn.get_unuseful_columns()
        try:
            data = pd.read_csv(
                # GBK is a more comprehensive superset of the GB2312 standard,
                # and it is often more compatible with a wider range of simplified Chinese characters
                # you might encounter in modern files. If one encoding doesn't work, try the other.
                file_path, skiprows=cls.num_skip_rows, encoding=cls.encoding
            ).drop(columns_to_drop, axis=1)
        except UnicodeDecodeError:
            # If not gbk, use utf-8
            cls.encoding = "utf-8"
            data = pd.read_csv(
                file_path,
                skiprows=cls.num_skip_rows,
                encoding=cls.encoding
            ).drop(columns_to_drop, axis=1)

        logger.info(f"Data (encoding={cls.encoding}) loaded successfull from file {file_path}")

        return data

    @override
    @classmethod
    def parse_row(cls, row: Series) -> Series:
        cashflow_direction = ALIPAY_CASHFLOW_DIRECTION[row[AlipayColumn.CASHFLOW_DIRECTION.column_name]]

        def derive_category() -> Category:
            category_column_name = AlipayColumn.CATEGORY.column_name

            def derive_to_unknown(_):
                logger.warning(f"Unknown Alipay category: {row}")
                return CategoryOutflow.UNKNOWN.name

            match cashflow_direction:
                case CashflowDirection.INFLOW:
                    return ALIPAY_INFLOW_CATEGORY_MAPPING.get(row[category_column_name], derive_to_unknown)(row)
                case CashflowDirection.OUTFLOW:
                    return ALIPAY_OUTFLOW_CATEGORY_MAPPING.get(row[category_column_name], derive_to_unknown)(row)
                case _:
                    return row[category_column_name]

        # Populate output
        output_row: Series = Series([])

        date: pd.Timestamp = pd.to_datetime(row[AlipayColumn.DATE_TIME.column_name])
        output_row[Column.DATE.value] = date

        output_row[Column.CATEGORY.value] = derive_category()
        output_row[Column.CATEGORY_RAW.value] = row[AlipayColumn.CATEGORY.column_name]

        output_row[Column.CURRENCY.value] = cls.currency.name
        output_row[Column.ACCOUNT.value] = cls.account.name

        output_row[Column.CASHFLOW_DIRECTION.value] = cashflow_direction.text
        output_row[Column.AMOUNT_ABSOLUTE.value] = row[AlipayColumn.AMOUNT.column_name]
        output_row[Column.AMOUNT_NET.value] = cashflow_direction * row[AlipayColumn.AMOUNT.column_name]

        output_row[Column.ACCOUNT_BALANCE.value] = "todo"
        output_row[Column.DESCRIPTION.value] = row[AlipayColumn.ITEM_DETAIL.column_name]
        output_row[Column.REMARK.value] = ""  # manual edit

        # TODO: handle aggregation; if aggregated, should have recored split to single items,
        # and the aggregated record should not be recorded in analysis
        output_row[Column.IS_AGGREGATED.value] = "todo"
        # TODO: think about how to show the refund item
        # should not be row[AlipayColumn.CATEGORY.column_name] == cls.refund_category
        output_row[Column.IS_REFUNDED.value] = "todo"

        return output_row


if __name__ == "__main__":
    # from pprint import pprint
    # pprint(AlipayParseStrategy.__dict__)

    test_log("Run from main.py to see the result")
