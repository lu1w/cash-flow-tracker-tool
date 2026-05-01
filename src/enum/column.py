from enum import Enum

from .cashflow_direction import CashflowDirection


class Column(Enum):
    '''Output columns'''
    DATE = "Date"
    CATEGORY = "Category"
    CATEGORY_RAW = "RAW Category"
    CURRENCY = "Currency"
    CASHFLOW_DIRECTION = f"{CashflowDirection.INFLOW.text}(+)/{CashflowDirection.OUTFLOW.text}(-)"
    AMOUNT_ABSOLUTE = "Absolute Amount"
    AMOUNT_NET = "Net Amount"
    ACCOUNT = "Account"
    ACCOUNT_BALANCE = "Account Balance"
    DETAILS = "Details"
    REMARK = "Remark"
    IS_AGGREGATED = "Is Aggregated"  # Means user need to manually
    IS_REFUND = "Is Refund"

    # def __init__(self, name):
    #     self.name = name


if __name__ == "__main__":
    assert Column.DATE.name == "DATE"
    assert Column.AMOUNT.value == "Amount"

    print(Column._member_names_)
