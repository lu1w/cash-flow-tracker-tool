from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category import Category, CategoryOutflow, CategoryInflow
from src.enum.category_resolver import CategoryResolver
from src.enum.currency import Currency


class TransactionEntryModel(BaseModel):
    """Represents a standardized cashflow entry."""

    # Date
    date: Annotated[datetime, Field(alias="Date")]

    # Category columns
    category: Annotated[CategoryInflow | CategoryOutflow, Field(alias="Category")]
    category_confidence: Annotated[float, Field(alias="Category Confidence")]
    category_resolver: Annotated[CategoryResolver, Field(alias="Category Resolver")]
    category_raw: Annotated[str, Field(alias="Raw Category")]

    # Monetary columns
    currency: Annotated[Currency, Field(alias="Currency")]
    cashflow_direction: Annotated[
        CashflowDirection,
        Field(alias=f"{CashflowDirection.INFLOW}(+)/{CashflowDirection.OUTFLOW}(-)")
    ]
    amount_absolute: Annotated[Decimal, Field(alias="Absolute Amount")]
    amount_net: Annotated[Decimal, Field(alias="Net Amount")]
    account: Annotated[Account, Field(alias="Account")]
    # TODO(PL23): support account balance computation; populate the data for the line below
    account_balance: Annotated[Decimal, Field(alias="Account Balance")] = Decimal(0)

    # Notes/text columns (Optional)
    description: Annotated[str, Field(default="", alias="Description")]  # The context for LLM
    remark: Annotated[str, Field(default="", alias="Remark")] = ""  # User's own notes

    # Boolean columns
    is_aggregated: Annotated[bool, Field(default=False, alias="Is Aggregated")] = False
    refunded: Annotated[bool, Field(default=False, alias="Refunded")] = False

    # =====

    # `use_enum_values` display the enum typed fields with only the enum value, not a key-value pair of enum.name and enum.value https://www.prefect.io/blog/pydantic-enums-introduction
    # `validate_by_name` allows model constructor __init__() to accept the field name instead of just the alias
    model_config = ConfigDict(use_enum_values=True, validate_by_name=True)

    class ConfigDict:
        # allows instantiating Pydantic model using either the field's python variable name or its defined alias
        populate_by_name = True

    @model_validator(mode="before")  # Runs before Pydantic’s internal parsing and validation
    @classmethod
    def strip_empty_strings(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Drops the key entirely if the value is an empty string, support default values to fill in
            return {k: v for k, v in values.items() if v != ""}
        return values
