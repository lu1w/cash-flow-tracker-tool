from enum import Enum
import pandas as pd
from typing import List

from .cashflow_direction import CashflowDirection


class Column(Enum):
    '''Output columns'''
    DATE = "Date"
    CATEGORY = "Category"
    CATEGORY_RAW = "RAW Category"  # Row category from the report files
    CURRENCY = "Currency"
    CASHFLOW_DIRECTION = f"{CashflowDirection.INFLOW.text}(+)/{CashflowDirection.OUTFLOW.text}(-)"
    AMOUNT_ABSOLUTE = "Absolute Amount"
    AMOUNT_NET = "Net Amount"
    ACCOUNT = "Account"
    ACCOUNT_BALANCE = "Account Balance"
    DETAILS = "Details"
    REMARK = "Remark"
    IS_AGGREGATED = "Is Aggregated"  # Means user need to manually
    IS_REFUNDED = "Refunded"

    # def __init__(self, name):
    #     self.name = name

    @staticmethod
    def verify_columns_data_type(df: pd.DataFrame) -> None:
        if not pd.api.types.is_datetime64_any_dtype(df[Column.DATE.value]):
            raise TypeError(f"DATE should have datetime64 type, but has type {df[Column.DATE.value].dtype}")


if __name__ == "__main__":
    assert Column.DATE.name == "DATE"
    assert Column.AMOUNT.value == "Amount"

    print(Column._member_names_)
