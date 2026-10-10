from pathlib import Path
from pydantic import BeforeValidator
from typing import Annotated, Set, Any
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Support import from project root
from src.utils.logger import logger


def clean_amount(value: str | Decimal) -> Decimal:
    """Cleanser for dollar amount records. Value will be a `str` if reading from files, be can be `Decimal` is passed in via the model's Python Constructor."""
    if isinstance(value, str):
        # Clean up formatting like "¥1,200.50" or " 100.00 "
        if not value[0].isnumeric():
            value = value[1:]
        cleaned = value.replace(",", "").strip()
        return Decimal(cleaned)
    return value


Amount = Annotated[Decimal, BeforeValidator(clean_amount)]


"""
Input models from different accounts.
"""

ignored_json_schema_metadata: dict[str, Any] = {"ignored": True}


class AlipayInputEntryModel(BaseModel):
    # Core Transaction Data (Required)
    date_time: datetime = Field(alias="交易时间")
    category: str = Field(alias="交易分类")
    counterparty: str = Field(alias="交易对方")
    item_detail: str = Field(alias="商品说明")
    cashflow_direction: str = Field(alias="收/支")  # You could also use a Custom Enum here (e.g., '收入' / '支出')
    amount: Amount = Field(alias="金额")
    payment_method: str = Field(alias="收/付款方式")  # Should usually be "账户余额"

    # Optional Metadata Columns (Safe if missing or empty string in CSV)
    counterparty_account: str = Field(default="", alias="对方账号", json_schema_extra=ignored_json_schema_metadata)
    transaction_status: str = Field(default="", alias="交易状态", json_schema_extra=ignored_json_schema_metadata)
    transaction_number: str = Field(default="", alias="交易订单号", json_schema_extra=ignored_json_schema_metadata)
    vendor_order_number: str = Field(default="", alias="商家订单号", json_schema_extra=ignored_json_schema_metadata)
    remark: str = Field(default="", alias="备注", json_schema_extra=ignored_json_schema_metadata)

    @classmethod
    def get_ignored_columns(cls) -> Set[str]:
        ignored = set()
        for field_name, field_info in cls.model_fields.items():
            # Check for our cleaner "ignore" flag instead of "is_useful"
            if isinstance(extra := field_info.json_schema_extra, dict) and extra.get("ignore") is True:
                # Use the alias if it exists (which should always be the case here);
                # fallback to the field variable name.
                if field_info.alias is not None:
                    ignored.add(field_info.alias)
                else:
                    logger.error(
                        f"{AlipayInputEntryModel}: No alias for {field_name} to clarify the data file column .")
        return ignored
