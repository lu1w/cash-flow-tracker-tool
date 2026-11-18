from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.enum.account import Account
from src.enum.cashflow_direction import CashflowDirection
from src.enum.category import Category, CategoryOutflow, CategoryInflow
from src.enum.currency import Currency


class TransactionEntryModel(BaseModel):
    """Represents a standardized cashflow entry."""

    # Date
    date: Annotated[datetime, Field(alias="Date")]

    # Category columns
    category: Annotated[CategoryInflow | CategoryOutflow, Field(alias="Category")]
    # TODO(PL29): remove resolver
    category_by_rules: Annotated[CategoryInflow | CategoryOutflow | None, Field(alias="Category (Rules)")] = None
    category_by_categorizer: Annotated[CategoryInflow | CategoryOutflow |
                                       None, Field(alias="Category (Categorizer)")] = None
    categorizer_confidence: Annotated[float, Field(alias="Categorizer Confidence")] = 0
    category_by_human: Annotated[CategoryInflow | CategoryOutflow | None, Field(alias="Category (Manual)")] = None
    category_raw: Annotated[str, Field(alias="Raw Category")]

    # Monetary columns
    account: Annotated[Account, Field(alias="Account")]
    currency: Annotated[Currency, Field(alias="Currency")]
    cashflow_direction: Annotated[
        CashflowDirection,
        Field(alias=f"{CashflowDirection.INFLOW}(+)/{CashflowDirection.OUTFLOW}(-)")
    ]
    amount_absolute: Annotated[Decimal, Field(alias="Absolute Amount")]
    amount_net: Annotated[Decimal, Field(alias="Net Amount")]
    # TODO(PL23): support account balance computation; populate the data for the line below
    account_balance: Annotated[Decimal, Field(alias="Account Balance")] = Decimal(0)

    # Notes/text columns (Optional)
    transaction_status: Annotated[str, Field(alias="Transaction Status")] = ""  # TODO(PL25): use this field
    description: Annotated[str, Field(alias="Description")] = ""  # The context for LLM
    remark: Annotated[str, Field(alias="Remark")] = ""  # User's own notes

    # Whether the trasaction needs to be break down into multiple items
    # TODO(PAB1): currently None represent not manually checked; later we can
    # support identify aggregation entries automatically? by then we just
    # need a bool
    is_aggregated: Annotated[bool | None, Field(alias="Is Aggregated")] = None

    # Whether the transaction is reverted
    refunded: Annotated[bool, Field(alias="Refunded")] = False

    # `use_enum_values`
    #   - display the enum typed fields with only the enum value, not a key-value pair of enum.name and enum.value https://www.prefect.io/blog/pydantic-enums-introduction
    #   - forces model.model_dump() to output the underlying raw values instead of the raw Enum objects
    # `validate_by_name`
    #   - allows model constructor __init__() to accept the field name instead of just the alias
    model_config = ConfigDict(use_enum_values=True, validate_by_name=True)

    @model_validator(mode="before")  # Runs before Pydantic’s internal parsing and validation
    @classmethod
    def strip_empty_strings(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Drops the key entirely if the value is an empty string, support default values to fill in
            return {k: v for k, v in values.items() if v != ""}
        return values
