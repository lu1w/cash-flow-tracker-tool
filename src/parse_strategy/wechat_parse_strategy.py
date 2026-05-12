
import sys
import pandas as pd
from enum import Enum
from pathlib import Path
from typing import List

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, test_log
from src.enum.account import Account
from src.enum.category import Category
from src.enum.column import Column
from src.enum.currency import Currency


class WechatColumn(Enum):
    '''Columns in a WeChat report file.'''
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


class WechatParseStrategy(ParseStrategyBase):
    account = Account.WECHAT
    currency = Currency.CNY
    file_extension = "xlsx"

    refund_category_keyword = "退款"

    @classmethod
    def load_data(cls, file_path: Path) -> pd.DataFrame:
        logger.info(f"Start loading data for file {file_path}")

        try:
            columns_to_drop = WechatColumn.get_unuseful_columns()
            data = pd.read_excel(file_path, skiprows=17).drop(columns_to_drop, axis=1)

            logger.info(f"Data (encoding={cls.encoding}) loaded successfull from file {file_path}.")
            return data
        except UnicodeDecodeError:
            logger.error(f"Error in decoding the data file ({file_path}): {e}")
        except Exception as e:
            logger.error(
                f"Error loading CSV ({file_path}): {e}")

    @classmethod
    def parse_row(cls, row: pd.Series) -> pd.Series:
        return row  # TODO

    @classmethod
    def fetch_input_file_date(cls, input_file_path: str) -> str:
        # `.data/wechat/微信支付账单流水文件(20251215-20260315)_20260315105929.xlsx` -> `(20251215-20260315)`
        return str(input_file_path).split('/')[-1][10:29]  # TODO: handle different separator for different OS


if __name__ == "__main__":
    WechatParseStrategy.execute()
