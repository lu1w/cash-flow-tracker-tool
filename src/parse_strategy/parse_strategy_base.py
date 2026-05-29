import sys
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.utils.logger import logger, test_log
from src.enum.account import Account
from src.enum.column import Column


class ParseStrategyBase(ABC):
    account = Account.UNKNOWN
    data_dir_path = Path(".data/REPLACE_ME")
    file_extension = "REPLACE_ME"

    monthly_cashflow: Dict[str, DataFrame] = {}

    should_validate_output_types = True

    @classmethod
    @abstractmethod
    def load_data(cls, file_path: Path) -> DataFrame:
        '''Read data from input file.'''
        pass

    @classmethod
    @abstractmethod
    def parse_row(cls, row: Series) -> Series:
        '''Core processing logic where the input data is mapped to the output data.'''
        pass

    @classmethod
    def get_data_dir_path(cls) -> Path:
        return Path(f".data/{str(cls.account.name).lower()}")

    @classmethod
    def get_output_dir_path(cls) -> Path:
        '''Defines where the output file should be stored.'''
        return Path(f".output/.{str(cls.account.name).lower()}")

    @classmethod
    def ensure_output_dir_path(cls) -> Path:
        output_dir_path = cls.get_output_dir_path()
        output_dir_path.mkdir(parents=True, exist_ok=True)
        return output_dir_path

    @classmethod
    def build_output_file_path(cls, date_key: str) -> str:
        # .output/.wechat/WECHAT(202602).csv
        return cls.ensure_output_dir_path() / f"{cls.account.name}({date_key}).csv"

    @classmethod
    def process_file(cls, file_path: Path) -> None:
        try:
            # Load data
            logger.info(f"Start loading data for file `{file_path}`")
            data: DataFrame = cls.load_data(file_path)

            # Parse data
            logger.info(f"Data loaded, start parsing rows for file `{file_path}`")
            parsed_data: DataFrame = data.apply(cls.parse_row, axis=1, result_type='reduce')
            if not cls.should_validate_output_types:
                Column.verify_columns_data_type(parsed_data)

            # Group data based on the year and month
            cls.monthly_cashflow = {f"{year:4}-{month:02}": row
                                    for (year, month), row
                                    in parsed_data.groupby([parsed_data['Date'].dt.year, parsed_data['Date'].dt.month])}

            # Writ data to monthly file
            logger.info(f"Rows parsed, start writing output for input file `{file_path}`")
            for year_month, df in cls.monthly_cashflow.items():
                df.to_csv(cls.build_output_file_path(year_month), index=False, encoding="utf-8", mode="w")

            logger.info(f"Successfully processed file `{file_path}`")
        except Exception as e:
            logger.error(f"Error in processing file `{file_path}`: {e}")

    @classmethod
    def execute(cls) -> None:
        data_dir_path = cls.get_data_dir_path()
        pattern = f"*.{cls.file_extension}"
        import os
        logger.info(f"Start parsing files with pattern {pattern} in {os.getcwd()}/{data_dir_path}")

        data_files_path = list(data_dir_path.glob(pattern=pattern))
        logger.info(f"All files to process: {[str(file_path) for file_path in data_files_path]}")

        for file_path in data_files_path:
            cls.process_file(file_path)

        # TODO: combine multiple accounts together
        # TODO: generate yearly file / analysis

        logger.info(f"Successfully processed all files in {data_dir_path}")


if __name__ == "__main__":
    from pprint import pprint
    pprint(ParseStrategyBase.__dict__)
