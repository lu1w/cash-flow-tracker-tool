from typing import override
import sys
import csv
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict, List, Any, TypeVar, Generic

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import FileConfig
from src.enum.account import Account
from src.enum.column import Column
from src.enum.currency import Currency
from src.models.input_model import AlipayInputEntryModel, WechatInputEntryModel, HsbcInputEntryModel
from src.models.transaction_entry_model import TransactionEntryModel
from src.utils.logger import logger, debug_log

InputEntryModelT = TypeVar("InputEntryModelT", AlipayInputEntryModel, WechatInputEntryModel, HsbcInputEntryModel)


class PreparseStrategyBase(ABC, Generic[InputEntryModelT]):
    """Abstract class that will be inherit by preparse strategies.
    The child class need to at least implement `load_data()` and `ensure_output_file_path()`.
    """

    # to be replaced
    account = Account.UNKNOWN

    encoding = "utf-8"
    file_extension = "csv"
    num_skip_rows = 0

    # optional config
    # require_data_type_validation = True

    @classmethod
    @abstractmethod
    def load_data(cls, file_path: Path) -> List[InputEntryModelT]:
        """Read data from input file."""
        pass

    @classmethod
    def get_input_data_dir_path(cls) -> Path:
        return Path(f"{FileConfig.INPUT_DATA_DIR}/{cls.account.dir_name}-raw")

    @classmethod
    @abstractmethod
    def ensure_output_file_path(cls, filename: str) -> Path:
        pass


class ParseStrategyBase(PreparseStrategyBase[InputEntryModelT], Generic[InputEntryModelT]):
    """Abstract class that will be inherit by preparse strategies.
    The child class need to at least implement `load_data()` and `parse_entry()`.
    """

    currency = Currency.UNKNOWN
    ignored_columns = set()

    @classmethod
    @abstractmethod
    def parse_entry(
        cls,
        input_entry_model: InputEntryModelT,
    ) -> TransactionEntryModel:
        pass

    @classmethod
    def _load_csv(
        cls,
        file_path: Path,
        encoding: str | None = None,
    ) -> List[Dict[str, Any]]:
        if encoding is None:
            encoding = cls.encoding

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
                {k: v for k, v in row.items() if k not in cls.ignored_columns}
                for row in reader
            ]
            logger.info(
                f"Data ({len(parsed_data)} rows, encoding {cls.encoding}) "
                f"loaded successfully from file {file_path}"
            )
            return parsed_data

    @override
    @classmethod
    def get_input_data_dir_path(cls) -> Path:
        return Path(f"{FileConfig.INPUT_DATA_DIR}/{cls.account.dir_name}")

    @override
    @classmethod
    def ensure_output_file_path(cls, filename: str) -> Path:
        standardized_dir_path = Path(f"{FileConfig.STANDARDIZED_DATA_DIR}/{cls.account.dir_name}")
        standardized_dir_path.mkdir(parents=True, exist_ok=True)
        # .data/standardized/.wechat/WECHAT(202602).csv
        return standardized_dir_path / filename


if __name__ == "__main__":
    from pprint import pprint
    pprint(ParseStrategyBase.__dict__)
