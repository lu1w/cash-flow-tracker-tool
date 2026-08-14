import sys
from enum import Enum
from pathlib import Path

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.currency import Currency

CASH = "cash"


class Account(Enum):
    UNKNOWN = ("(unknown)", Currency.UNKNOWN)
    ALIPAY = ("Alipay", Currency.CNY)
    WECHAT = ("Wechat", Currency.CNY)
    HSBC_HKD = ("HSBC", Currency.HKD)

    CASH_AUD = (CASH, Currency.AUD)
    CASH_CNY = (CASH, Currency.CNY)
    CASH_HKD = (CASH, Currency.HKD)
    CASH_JPY = (CASH, Currency.JPY)
    CASH_TWD = (CASH, Currency.TWD)
    CASH_USD = (CASH, Currency.USD)

    def __init__(self, account_type: str, currency: Currency):
        """Setting attributes for the enum"""
        self.account_type = account_type
        self.currency = currency

    # def __str__(self):
    #     if self.account_type in ["cash", "HSBC"]:
    #         return f"{self.account_type} ({self.currency.name})"

    @property
    def value(self):
        if self.account_type in ["cash", "HSBC"]:
            return f"{self.account_type} ({self.currency.name})"
        return f"{self.account_type}"

    @property
    def dir_name(self):
        return self.name.lower()


ALL_ACTIVE_ACCOUNTS = (Account.ALIPAY, Account.WECHAT, Account.HSBC_HKD)

# Tests:
if __name__ == "__main__":
    # assert str(Account.HSBC_HKD) == "HSBC (HKD)"
    assert Account.CASH_CNY.value == f"{CASH} (CNY)"
    assert Account.CASH_AUD.name == "CASH_AUD"
    assert Account.ALIPAY.name == "ALIPAY"
