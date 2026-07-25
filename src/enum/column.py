import sys
from pathlib import Path
from enum import StrEnum
import pandas as pd
from typing import List

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.cashflow_direction import CashflowDirection

# TODO: utilize pydantic library to create a typed model for each row, instead of using enum to model the columns


# NOTE: need to inherit from `StrEnum` so that Column.X can resolve to Column.X.value directly
class Column(StrEnum):
    """Output columns"""
    DATE = "Date"

    # Category columns
    CATEGORY = "Category"
    CATEGORY_CONFIDENCE = "Category Confidence"
    CATEGORY_RESOLVER = "Category Resolver"
    CATEGORY_RAW = "Raw Category"  # Category from the report files without changes

    # Monetary columns
    CURRENCY = "Currency"
    CASHFLOW_DIRECTION = f"{CashflowDirection.INFLOW.text}(+)/{CashflowDirection.OUTFLOW.text}(-)"
    AMOUNT_ABSOLUTE = "Absolute Amount"
    AMOUNT_NET = "Net Amount"
    ACCOUNT = "Account"
    ACCOUNT_BALANCE = "Account Balance"

    # Notes/text columns
    REMARK = "Remark"  # User notes for oneself
    DESCRIPTION = "Description"  # Used as the context and description of the entry for LLM

    # Means user need to manually split the record into multiple records, and
    # the aggregated record should not be used in analysis
    IS_AGGREGATED = "Is Aggregated"

    # Refunded records that indicate the original record has been refunded,
    # and the refunded record should be treated as no money spent, and not be used in analysis
    IS_REFUNDED = "Refunded"

    @staticmethod
    def verify_columns_data_type(df: pd.DataFrame) -> None:
        if not pd.api.types.is_datetime64_any_dtype(df[Column.DATE.value]):
            raise TypeError(f"DATE should have datetime64 type, but has type {df[Column.DATE.value].dtype}")


if __name__ == "__main__":
    print()
    assert Column.DATE.name == "DATE"
    assert Column.ACCOUNT.value == "Account"
    assert str(Column.ACCOUNT) == "Account"
    assert Column.CATEGORY_RESOLVER == "Category Resolver"

    print(Column._member_names_)
