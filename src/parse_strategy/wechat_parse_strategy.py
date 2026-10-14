
from transformers import Wav2Vec2PhonemeCTCTokenizer
import sys
import pandas as pd
from enum import Enum
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, override
from pydantic import TypeAdapter

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.parse_strategy.parse_strategy_base import PreparseStrategyBase, ParseStrategyBase
from src.utils.logger import logger, debug_log
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category_resolver import CategoryResolver
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.column import Column
from src.enum.currency import Currency
from src.config.config import FileConfig
from src.models.input_model import WechatInputEntryModel
from src.models.transaction_entry_model import TransactionEntryModel


class WechatPreparseStrategy(PreparseStrategyBase[WechatInputEntryModel]):
    account = Account.WECHAT
    file_extension = "xlsx"
    num_skip_rows = 17

    @override
    @classmethod
    def ensure_output_file_path(cls, filename: str) -> Path:
        output_dir_path = Path(f"{FileConfig.INPUT_DATA_DIR}/{cls.account.dir_name}")
        output_dir_path.mkdir(parents=True, exist_ok=True)
        return output_dir_path / filename

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> List[WechatInputEntryModel]:
        df: pd.DataFrame = pd.read_excel(file_path, skiprows=cls.num_skip_rows)
        rows = df.to_dict(orient="records")
        entry_models = TypeAdapter(list[WechatInputEntryModel]).validate_python(rows)
        return entry_models

    @classmethod
    def parse_row(cls, row: pd.Series) -> pd.Series:
        # need to have date column for grouping into monthly file
        # date: pd.Timestamp = pd.to_datetime(row[WechatColumn.DATE_TIME.column_name])
        # row[Column.DATE.value] = date
        return row


class WechatCashflowDirection(Enum):
    INFLOW = "收入"
    OUTFLOW = "支出"


class WechatParseStrategy(ParseStrategyBase):
    account = Account.WECHAT
    currency = Currency.CNY
    file_extension = "csv"
    num_skip_rows = 0

    refund_category_keyword = "退款"
    ignored_columns = WechatInputEntryModel.get_ignored_columns()

    WECHAT_CASHFLOW_DIRECTION_MAPPING: Dict[str, CashflowDirection] = {
        WechatCashflowDirection.INFLOW.value: CashflowDirection.INFLOW,
        WechatCashflowDirection.OUTFLOW.value: CashflowDirection.OUTFLOW,
    }

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> List[WechatInputEntryModel]:
        data_rows = cls._load_csv(file_path, cls.encoding)
        entry_models = [WechatInputEntryModel.model_validate(row) for row in data_rows]
        return entry_models

    @override
    @classmethod
    def parse_entry(cls, input_entry_model: WechatInputEntryModel) -> TransactionEntryModel:
        # Cashflow Direction
        cashflow_direction = (
            cls.WECHAT_CASHFLOW_DIRECTION_MAPPING.get(input_entry_model.cashflow_direction)
            or CashflowDirection.get_unknown(input_entry_model)
        )

        # Derive Standardized Category
        def derive_category() -> CategoryInflow | CategoryOutflow:
            match input_entry_model.cashflow_direction:
                case WechatCashflowDirection.INFLOW.value:
                    return CategoryInflow.UNKNOWN
                case WechatCashflowDirection.OUTFLOW.value:
                    if "滴滴出行" in input_entry_model.counterparty:
                        return CategoryOutflow.TRANSPORTATION
                    return CategoryOutflow.UNKNOWN
                case _:
                    # Using OUTFLOW.UNKNOWN as a safe typing fallback for unhandled directions
                    return CategoryOutflow.UNKNOWN

        return TransactionEntryModel(
            date=input_entry_model.date_time,
            category=derive_category(),
            category_confidence=0.1,
            category_resolver=CategoryResolver.RULES,
            category_raw=f"{input_entry_model.category} - {input_entry_model.counterparty}",
            account=cls.account,  # Assuming account configuration lives on Strategy class
            currency=cls.currency,  # Assuming currency configuration lives on Strategy class
            cashflow_direction=cashflow_direction,
            amount_absolute=input_entry_model.amount,
            amount_net=input_entry_model.amount * cashflow_direction,
            account_balance=Decimal("0.0"),  # TODO(PL23): Implement runtime balance computation pipeline
            transaction_status=input_entry_model.transaction_status,
            description=input_entry_model.item_detail,
            remark=input_entry_model.remark or "",
            is_aggregated=None,  # TODO: Handle item-splitting / aggregation checks
            refunded=None        # TODO: Implement refund parsing logic here
        )
