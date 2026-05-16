import sys
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series

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
    @abstractmethod
    def fetch_input_file_date(cls, input_file_path: str, start_date, end_date) -> str:
        # TODO: store the data (Dataframe) as instance variable, so the child
        # class can fetch the start/end date, and don't need to pass in two
        # different logic to get the input file date.
        # We want to use the input file path when possible, since the cashflow
        # only reflects the date where cashlow happened.
        # Or Maybe just manually rename the HSBC files, so we don't rely on cashflow dates.
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
    def build_output_file_path(cls, input_file_path: str, start_date: str, end_date: str) -> str:
        file_date = cls.fetch_input_file_date(input_file_path, start_date, end_date)

        # .output/.wechat/WECHAT(20251215-20260315).csv
        return cls.ensure_output_dir_path() / f"{cls.account.name}{file_date}.csv"

    @classmethod
    def process_file(cls, file_path: Path) -> None:
        try:
            logger.info(f"Start loading data for file `{file_path}`")
            data: DataFrame = cls.load_data(file_path)

            logger.info(f"Data loaded, start parsing rows for file `{file_path}`")
            parsed_data: DataFrame = data.apply(cls.parse_row, axis=1, result_type='reduce')
            Column.verify_columns_data_type(parsed_data)

            # Get starting date and end date
            start_date: pd.Timestamp = parsed_data.loc[len(parsed_data) - 1].loc[Column.DATE.value]
            end_date: pd.Timestamp = parsed_data.loc[0].loc[Column.DATE.value]

            logger.info(f"Rows parsed, start writing output for input file `{file_path}`")
            parsed_data.to_csv(
                cls.build_output_file_path(file_path, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")),
                index=False,
                encoding="utf-8",
                mode="w"
            )

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
