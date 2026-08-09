
import sys
import pandas as pd
from enum import Enum
from pathlib import Path
from typing import List, Dict, override

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, test_log
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.column import Column
from src.enum.currency import Currency


class WechatColumn(Enum):
    """Columns in a WeChat report file."""
    # 交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注
    DATE_TIME = ("交易时间", True)
    CATEGORY = ("交易类型", True)
    COUNTERPARTY = ("交易对方", True)
    ITEM_DETAIL = ("商品", True)
    CASHFLOW_DIRECTION = ("收/支", True)
    AMOUNT = ("金额(元)", True)
    PAYMENT_METHOD = ("支付方式", False)
    TRANSACTION_STATUS = ("当前状态", False)
    TRANSACTION_NUMBER = ("交易单号", False)
    VENDOR_ORDER_NUMBER = ("商户单号", False)
    REMARK = ("备注", False)

    def __init__(self, column_name: str, is_useful: bool):
        self.column_name = column_name
        self.is_useful = is_useful

    def get_unuseful_columns() -> List[str]:
        return [column.column_name for column in WechatColumn if not column.is_useful]


class WechatCashflowDirection(Enum):
    INFLOW = "收入"
    OUTFLOW = "支出"


WECHAT_CASHFLOW_DIRECTION_MAPPING: Dict[str, CashflowDirection] = {
    WechatCashflowDirection.INFLOW.value: CashflowDirection.INFLOW,
    WechatCashflowDirection.OUTFLOW.value: CashflowDirection.OUTFLOW,
}


class WechatParseStrategy(ParseStrategyBase):
    account = Account.WECHAT
    currency = Currency.CNY
    file_extension = "xlsx"

    refund_category_keyword = "退款"

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> pd.DataFrame:
        try:
            columns_to_drop = WechatColumn.get_unuseful_columns()
            data = pd.read_excel(file_path, skiprows=17).drop(columns_to_drop, axis=1)
            return data
        except UnicodeDecodeError as e:
            # FIXME: missing `return` here — falls through to implicit `return None`, which then
            # raises a confusing AttributeError in Parser._process_file and masks this real error.
            logger.exception(f"Error in decoding the data file `{file_path}`: {e}")

    @override
    @classmethod
    def parse_row(cls, row: pd.Series) -> pd.Series:
        cashflow_direction = \
            WECHAT_CASHFLOW_DIRECTION_MAPPING.get(row[WechatColumn.CASHFLOW_DIRECTION.column_name]) \
            or CashflowDirection.get_unknown(row)

        # FIXME: derive_category() is fully implemented below but never called — parse_row hardcodes
        # Category to "TODO: check items description" instead (see below), so every WeChat
        # transaction is permanently mis-categorized and never picked up by the embedding
        # categorizer (which only targets rows with an empty-string category).
        def derive_category() -> Category:
            match row[WechatColumn.CASHFLOW_DIRECTION.column_name]:
                case WechatCashflowDirection.INFLOW.value:
                    pass  # FIXME: falls through and implicitly returns None instead of a category
                case WechatCashflowDirection.OUTFLOW.value:
                    if (
                        "滴滴出行" in row[WechatColumn.COUNTERPARTY.column_name]
                    ):
                        return CategoryOutflow.TRANSPORTATION

                    if (
                        "普拉提瑜伽工作室" in row[WechatColumn.COUNTERPARTY.column_name]
                    ):
                        return CategoryOutflow.FITNESS
                case _:
                    raise Exception(f"Unknown cashflow direction: {row}")

        # Populate output
        output_row: pd.Series = pd.Series([])

        date: pd.Timestamp = pd.to_datetime(row[WechatColumn.DATE_TIME.column_name])
        output_row[Column.DATE.value] = date

        # Wechat category does not tell anything, need to refer to the ITEM_DETAIL column
        # NOTE: should be REFUND if cls.refund_category_keyword in row[WechatColumn.CATEGORY.column_name]
        output_row[Column.CATEGORY.value] = "TODO: check items description"
        output_row[Column.CATEGORY_RAW.value] = row[WechatColumn.CATEGORY.column_name]

        output_row[Column.CURRENCY.value] = cls.currency.name
        output_row[Column.ACCOUNT.value] = cls.account.name

        output_row[Column.CASHFLOW_DIRECTION.value] = cashflow_direction.text
        output_row[Column.AMOUNT_ABSOLUTE.value] = row[WechatColumn.AMOUNT.column_name]
        output_row[Column.AMOUNT_NET.value] = cashflow_direction * row[WechatColumn.AMOUNT.column_name]

        output_row[Column.ACCOUNT_BALANCE.value] = "todo"
        output_row[Column.DESCRIPTION.value] = row[WechatColumn.ITEM_DETAIL.column_name]
        output_row[Column.REMARK.value] = "--"

        # TODO: handle aggregation; if aggregated, should have recored split to single items,
        # and the aggregated record should not be recorded in analysis
        output_row[Column.IS_AGGREGATED.value] = "todo"
        # TODO: think about how to show the refund item
        output_row[Column.IS_REFUNDED.value] = "todo"

        return output_row


class WechatRawParseStrategy(WechatParseStrategy):
    require_data_type_validation = False

    @classmethod
    def parse_row(cls, row: pd.Series) -> pd.Series:

        # need to have date column for grouping into monthly file
        date: pd.Timestamp = pd.to_datetime(row[WechatColumn.DATE_TIME.column_name])
        row[Column.DATE.value] = date

        return row

    @classmethod
    def get_parsed_data_dir_path(cls) -> Path:
        from src.config.config import FileConfig
        return Path(f"{FileConfig.INPUT_DATA_DIR}/.{str(cls.account.name).lower()}-csv")


if __name__ == "__main__":
    test_log("Run from main.py to see the result")
