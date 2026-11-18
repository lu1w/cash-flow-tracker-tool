
import sys
from enum import Enum
from pathlib import Path

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
from src.models.transaction_entry_model import TransactionEntryModel
from src.parse_strategy.parse_strategy_base import ParseStrategyBase
from src.utils.logger import logger, debug_log


class AlipayParseStrategy(ParseStrategyBase[AlipayInputEntryModel]):
    """Parsing strategy for handling Alipay transaction history data."""

    account = Account.ALIPAY
    currency = Currency.CNY
    file_extension = "csv"
    encoding = 'gbk'

    # refund_category = "退款"

    num_skip_rows = 23
    ignored_columns = AlipayInputEntryModel.get_ignored_columns()

    ALIPAY_CASHFLOW_DIRECTION: Dict[str, CashflowDirection] = {
        "收入": CashflowDirection.INFLOW,
        "支出": CashflowDirection.OUTFLOW,
        "不计收支": CashflowDirection.UNKNOWN  # TODO(PL24): check why does this show up in the data
    }

    ALIPAY_INFLOW_CATEGORY_MAPPING: Dict[str, Callable[[AlipayInputEntryModel], CategoryInflow]] = {
        "退款": lambda _: CategoryInflow.REFUND,
        "转账红包": lambda entry_model: CategoryInflow.TRANSACTION if entry_model.item_detail == "转账" else CategoryInflow.GIFT
    }

    ALIPAY_OUTFLOW_CATEGORY_MAPPING: Dict[str, Callable[[AlipayInputEntryModel], CategoryOutflow]] = {
        "交通出行": lambda _: CategoryOutflow.TRANSPORTATION,
        "日用百货": lambda _: CategoryOutflow.LIVING,
        "家居家装": lambda _: CategoryOutflow.LIVING,
        "生活服务": lambda _: CategoryOutflow.LIVING,
        "餐饮美食": lambda _: CategoryOutflow.FOOD,
        "酒店旅游": lambda _: CategoryOutflow.HOUSING,
        "教育培训": lambda _: CategoryOutflow.PERSONAL_GROWTH,
        "运动户外": lambda _: CategoryOutflow.FITNESS,
        "服饰装扮": lambda _: CategoryOutflow.CLOTHING_AND_ACCESSORIES,
        "美容美发": lambda _: CategoryOutflow.BEAUTY,
        "数码电器": lambda _: CategoryOutflow.ELECTRONICS,
        "充值缴费": lambda entry_model: CategoryOutflow.TELECOMMUNICATION if entry_model.counterparty == "中国移动" else CategoryOutflow.UNKNOWN,
        "住房物业": lambda _: CategoryOutflow.UNKNOWN,
        "医疗健康": lambda _: CategoryOutflow.UNKNOWN,
        "文化休闲": lambda _: CategoryOutflow.UNKNOWN,
        "商业服务": lambda _: CategoryOutflow.UNKNOWN,
        "其他": lambda _: CategoryOutflow.UNKNOWN,
    }

    @override
    @classmethod
    def load_data(cls, file_path: Path) -> List[AlipayInputEntryModel]:
        try:
            data_rows = cls._load_csv(file_path, cls.encoding)
        except UnicodeDecodeError:
            # If the original encoding fails (e.g. GBK), fallback to utf-8
            cls.encoding = "utf-8"
            data_rows = cls._load_csv(file_path, cls.encoding)

        entry_models = [AlipayInputEntryModel.model_validate(row) for row in data_rows]
        return entry_models

    @override
    @classmethod
    def parse_entry(
        cls,
        input_entry_model: AlipayInputEntryModel,
    ) -> TransactionEntryModel:
        raw_amount = input_entry_model.amount
        cashflow_direction = AlipayParseStrategy.ALIPAY_CASHFLOW_DIRECTION[input_entry_model.cashflow_direction]

        def derive_category() -> CategoryInflow | CategoryOutflow:
            category: str = input_entry_model.category

            def derive_to_unknown(entry_model, default_category: CategoryInflow | CategoryOutflow):
                logger.warning(f"Unknown Alipay category: \n{entry_model}")
                return default_category

            match cashflow_direction:
                case CashflowDirection.INFLOW:
                    return (cls.ALIPAY_INFLOW_CATEGORY_MAPPING.get(
                        category,
                        lambda row: derive_to_unknown(row, CategoryInflow.UNKNOWN)
                    )(input_entry_model))
                case CashflowDirection.OUTFLOW:
                    return (cls.ALIPAY_OUTFLOW_CATEGORY_MAPPING.get(
                        category,
                        lambda row: derive_to_unknown(row, CategoryOutflow.UNKNOWN)
                    )(input_entry_model))
                case _:
                    return CategoryOutflow.UNKNOWN  # TODO(PL9): have a generic unknown category

        return TransactionEntryModel(
            date=input_entry_model.date_time,
            category=derive_category(),
            category_confidence=0.1,
            category_resolver=CategoryResolver.RULES,
            category_raw=input_entry_model.category,
            currency=cls.currency,
            account=cls.account,
            cashflow_direction=cashflow_direction,
            amount_absolute=raw_amount,
            amount_net=cashflow_direction * raw_amount,
            description=input_entry_model.item_detail,
            is_aggregated=None,  # TODO(PAB1): implement aggregation entry identificaiton
        )
