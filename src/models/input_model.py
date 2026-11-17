from pathlib import Path
from pydantic import BeforeValidator
from typing import Annotated, Set, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

if __name__ == "__main__":
    # Support import from project root
    import sys
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.append(project_root)


# Support import from project root
from src.utils.logger import logger


def clean_amount(value: str | Decimal) -> Decimal:
    """Cleanser for dollar amount records. Value is a `str` when read from files, or a `Decimal` when passed to the model constructor."""
    if isinstance(value, str):
        # Clean up formatting like "¥1,200.50", "-1,234.56", or " 100.00 ".
        # Keep a leading sign; only drop a currency symbol.
        cleaned = value.strip().replace(",", "")
        if cleaned and not cleaned[0].isnumeric() and cleaned[0] not in "+-":
            cleaned = cleaned[1:].strip()
        return Decimal(cleaned)
    return value


Amount = Annotated[Decimal, BeforeValidator(clean_amount)]


IGNORED_METADATA_KEY = "ignored"
IGNORED_JSON_SCHEMA_METADATA: dict[str, Any] = {IGNORED_METADATA_KEY: True}


"""
Input models from different accounts.
"""


class InputEntryBaseModel(BaseModel):
    @classmethod
    def get_ignored_columns(cls) -> Set[str]:
        """Returns a list of the original Chinese column headers (aliases) that are ignored."""
        ignored = set()
        for field_info in cls.model_fields.values():
            # Check if json_schema_extra exists and has "ignored": True
            if isinstance(extra := field_info.json_schema_extra, dict) and extra.get(IGNORED_METADATA_KEY) is True:
                ignored.add(field_info.alias or field_info.default)
        logger.info(f"Ignored columns for {cls.__name__} is: {ignored}")
        return ignored


class AlipayInputEntryModel(InputEntryBaseModel):
    """Pydantic model representing a row from an Alipay transaction report."""

    date_time: Annotated[datetime, Field(alias="交易时间")]
    category: Annotated[str, Field(alias="交易分类")]
    counterparty: Annotated[str, Field(alias="交易对方")]
    item_detail: Annotated[str, Field(alias="商品说明")]
    cashflow_direction: Annotated[str, Field(alias="收/支")]
    amount: Annotated[Amount, Field(alias="金额")]
    payment_method: Annotated[str, Field(alias="收/付款方式")]  # Should usually be "账户余额"
    transaction_status: Annotated[str, Field(alias="交易状态")]
    remark: Annotated[str, Field(alias="备注")] = ""

    # Ignored Columns (skip reading these values when loading the data file)
    counterparty_account: Annotated[str, Field(alias="对方账号", json_schema_extra=IGNORED_JSON_SCHEMA_METADATA)] = ""
    transaction_number: Annotated[str, Field(alias="交易订单号", json_schema_extra=IGNORED_JSON_SCHEMA_METADATA)] = ""
    vendor_order_number: Annotated[str, Field(alias="商家订单号", json_schema_extra=IGNORED_JSON_SCHEMA_METADATA)] = ""


class WechatInputEntryModel(InputEntryBaseModel):
    """Pydantic model representing a row from a WeChat transaction report."""

    # Useful fields
    date_time: Annotated[datetime, Field(alias="交易时间")]
    category: Annotated[str, Field(alias="交易类型")]
    counterparty: Annotated[str, Field(alias="交易对方")]
    item_detail: Annotated[str, Field(alias="商品")]
    cashflow_direction: Annotated[str, Field(alias="收/支")]
    amount: Annotated[Amount, Field(alias="金额(元)")]
    payment_method: Annotated[str, Field(alias="支付方式")]  # usually "零钱"
    transaction_status: Annotated[str, Field(alias="当前状态")]
    remark: Annotated[str, Field(alias="备注")] = ""

    # Ignored fields
    transaction_number: Annotated[str, Field(alias="交易单号", json_schema_extra=IGNORED_JSON_SCHEMA_METADATA)] = ""
    vendor_order_number: Annotated[str, Field(alias="商户单号", json_schema_extra=IGNORED_JSON_SCHEMA_METADATA)] = ""

    # model_config = {
    #     "populate_by_name": True  # Allows initialization by field name or alias
    # }

    @field_validator('transaction_number', "vendor_order_number", mode='before')
    @classmethod
    def convert_int_to_str(cls, v):
        if not isinstance(v, str):
            return str(v)
        return v


class HsbcInputEntryModel(InputEntryBaseModel):
    """Pydantic model representing a parsed row from an HSBC report."""

    date: Annotated[date, Field(alias="Date")]
    item_detail: Annotated[str, Field(alias="Description")]
    net_amount: Annotated[Amount, Field(alias="Billing amount")]
    currency: Annotated[str, Field(alias="Billing currency")]
    balance: Annotated[Amount, Field(alias="Balance")]
    balance_currency: Annotated[str, Field(alias="Balance currency")]

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        # HSBC exports dates as `dd/mm/yyyy` and has no time component.
        if isinstance(value, str):
            return datetime.strptime(value.strip(), "%d/%m/%Y").date()
        return value


if __name__ == "__main__":
    ignored = AlipayInputEntryModel.get_ignored_columns()
