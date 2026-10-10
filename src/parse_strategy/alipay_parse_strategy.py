
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
from src.models.transaction_entry_model import TransactionEntryModel
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

    @classmethod
    def load_data_models(cls, file_path: Path) -> List[AlipayInputEntryModel]:
        return [AlipayInputEntryModel.model_validate(row)
                for row in cls._load_data_rows(file_path)]

    @classmethod
    def _load_data_rows(cls, file_path: Path) -> List[Dict[str, Any]]:
        columns_to_drop = set(AlipayInputEntryModel.get_ignored_columns())

        try:
            data = cls._load_csv(file_path, cls.encoding, columns_to_drop)
        except UnicodeDecodeError:
            # If the original encoding fails (e.g. GBK), fallback to utf-8
            cls.encoding = "utf-8"
            data = cls._load_csv(file_path, cls.encoding, columns_to_drop)

        logger.info(f"Data (encoding={cls.encoding}) loaded successfully from file {file_path}")
        return data

    @classmethod
    def _load_csv(cls, file_path: Path, encoding: str, columns_to_drop: set = set()) -> List[Dict[str, Any]]:
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

    @classmethod
    def parse_entry(
        cls,
        input_entry_model: AlipayInputEntryModel,
    ) -> TransactionEntryModel:

        # Extract data using your original config safely
        raw_amount = input_entry_model.amount  # float(row[AlipayColumn.AMOUNT.column_name])

        # Assuming cashflow_direction behaves like a multiplier when multiplying numeric types
        # (e.g. -1 for outbound, 1 for inbound)
        cashflow_direction = AlipayParseStrategy.ALIPAY_CASHFLOW_DIRECTION[input_entry_model.cashflow_direction]
        # net_multiplier = int(cashflow_direction)

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
            # pd.to_datetime(row[AlipayColumn.DATE_TIME.column_name]).to_pydatetime(),
            category=derive_category(),
            category_confidence=0.1,
            category_resolver=CategoryResolver.RULES,
            category_raw=input_entry_model.category,  # str(row[AlipayColumn.CATEGORY.column_name]),
            currency=cls.currency,
            account=cls.account,
            cashflow_direction=cashflow_direction,
            amount_absolute=raw_amount,
            amount_net=cashflow_direction * raw_amount,
            description=input_entry_model.item_detail,  # str(row[AlipayColumn.ITEM_DETAIL.column_name]),
            # Fields like account_balance, remark, is_aggregated, is_refunded
            # fallback onto the model's empty string defaults automatically!
        )
