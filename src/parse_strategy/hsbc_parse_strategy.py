import sys
from datetime import datetime, time
from decimal import Decimal
from pathlib import Path
from typing import List, override


# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category import CategoryInflow, CategoryOutflow
from src.enum.category_resolver import CategoryResolver
from src.enum.currency import Currency
from src.models.input_model import HsbcInputEntryModel
from src.models.transaction_entry_model import TransactionEntryModel
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger


class HsbcParseStrategy(ParseStrategyBase[HsbcInputEntryModel]):
    """Parsing strategy for HSBC transaction history."""

    account = Account.HSBC_HKD
    # TODO(PL27): support multiple HSBC accounts with different currencies; this may need to become an instance field
    currency = Currency.HKD
    file_extension = "csv"
    encoding = "utf-8"

    cash_rebate_keyword = "CREDIT AS ADVISED"

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> List[HsbcInputEntryModel]:
        data_rows = cls._load_csv(file_path, cls.encoding)
        return [HsbcInputEntryModel.model_validate(row) for row in data_rows]

    @override
    @classmethod
    def parse_entry(cls, input_entry_model: HsbcInputEntryModel) -> TransactionEntryModel:
        net_amount: Decimal = input_entry_model.net_amount
        # HSBC stores the sign on the billing amount. A leading minus is an outflow.
        cashflow_direction = CashflowDirection.OUTFLOW if net_amount < 0 else CashflowDirection.INFLOW

        def derive_category() -> CategoryInflow | CategoryOutflow:
            if cls.cash_rebate_keyword in input_entry_model.item_detail:
                return CategoryInflow.CASH_REBATE
            if cashflow_direction == CashflowDirection.INFLOW:
                return CategoryInflow.UNKNOWN
            return CategoryOutflow.UNKNOWN

        # HSBC dates have no time. Store midnight so the standardized column stays a datetime.
        date = datetime.combine(input_entry_model.date, time.min)

        return TransactionEntryModel(
            date=date,
            category=derive_category(),
            category_confidence=0.1,
            category_resolver=CategoryResolver.RULES,
            category_raw=input_entry_model.item_detail,  # no "" since pydantic rejects emptry string for literal type
            currency=cls.currency,
            account=cls.account,
            cashflow_direction=cashflow_direction,
            amount_absolute=abs(net_amount),
            amount_net=net_amount,
            account_balance=input_entry_model.balance,
            description=input_entry_model.item_detail,
            remark="",
            is_aggregated=False,  # TODO(PAB1): handle aggregation check
            refunded=False,  # TODO(PAB2): handle refund update
        )
