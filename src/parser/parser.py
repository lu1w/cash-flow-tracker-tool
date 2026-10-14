import sys
import os
import csv
from pathlib import Path
import pandas as pd
from pandas import DataFrame, Series
from typing import Dict, List, Generic, override

# Support import from project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import ParserConfig
from src.parse_strategy.parse_strategy_base import PreparseStrategyBase, ParseStrategyBase, InputEntryModelT
from src.models.transaction_entry_model import TransactionEntryModel
from src.utils.filename_util import get_year_month_key
from src.utils.logger import logger, debug_log
from src.enum.column import Column


class Preparser(Generic[InputEntryModelT]):
    def __init__(self, preparse_strategy: PreparseStrategyBase[InputEntryModelT]):
        self.parse_strategy = preparse_strategy

    def _process_file(self, file_path: Path) -> None:
        try:
            # Load data
            logger.info(f"Start loading data for file `{file_path}`")
            entries = self.parse_strategy.load_data(file_path)

            logger.info(f"Data loaded, start preparsing file `{file_path}`")

            preparsed_file = self.parse_strategy.ensure_output_file_path(f"{file_path.stem}.csv")
            logger.info(f"Writing {len(entries)} entries to {preparsed_file}")

            headers = list(entries[0].model_dump(by_alias=True).keys())
            with open(preparsed_file, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry.model_dump(by_alias=True))

            # # If using Dataframe:
            # df.to_csv(self.parse_strategy.ensure_output_file_path(year_month),
            #           index=False, encoding="utf-8", mode="w")

            logger.info(f"Successfully preparsed file `{file_path}` to {preparsed_file}")
        except Exception as e:
            logger.exception(f"Error when preparsing file `{file_path}`: {e}")

    def execute(self) -> None:
        """Get the files from the input data directory, and parse into standardized format."""

        input_data_dir_path = self.parse_strategy.get_input_data_dir_path()
        pattern = f"[!_]*.{self.parse_strategy.file_extension}"
        data_file_paths = list(input_data_dir_path.glob(pattern=pattern))

        logger.info(
            f"Start parsing files with pattern {pattern} in {os.getcwd()}/{input_data_dir_path}: \n"
            + f"{'\n'.join(['- ' + str(file_path) for file_path in data_file_paths])}")

        for file_path in data_file_paths:
            # TODO: currently each file overwrites the previous files' monthly file if the month has overlaps; fix this
            self._process_file(file_path)

        # TODO: combine multiple accounts together
        # TODO: generate yearly file? / analysis

        logger.info(f"Successfully processed all files in {input_data_dir_path} with pattern {pattern}")


class Parser(Preparser, Generic[InputEntryModelT]):
    def __init__(self, parse_strategy: ParseStrategyBase[InputEntryModelT]):
        self.parse_strategy: ParseStrategyBase[InputEntryModelT] = parse_strategy

    @override
    def _process_file(self, file_path: Path) -> None:
        try:
            # Load data
            logger.info(f"Start loading data for file `{file_path}`")
            entries = self.parse_strategy.load_data(file_path)

            logger.info(f"Data loaded, start parsing file `{file_path}`")

            # Parse data
            parsed_data_entries: List[TransactionEntryModel] = [self.parse_strategy.parse_entry(entry)
                                                                for entry in entries]

            # Group data based on the year and month
            monthly_cashflows: Dict[str, list[TransactionEntryModel]] = {}
            for entry in parsed_data_entries:
                year_month_key = get_year_month_key(entry.date.year, entry.date.month)
                if year_month_key in monthly_cashflows:
                    monthly_cashflows[year_month_key].append(entry)
                else:
                    monthly_cashflows[year_month_key] = [entry]

            # Write data to monthly files
            fieldnames = [
                # potentialy cleaner version: model_json_schema()['properties'] extracts the aliases automatically
                # fieldnames = list(UserProfile.model_json_schema(by_alias=True)["properties"].keys())
                field.alias or name
                for name, field in TransactionEntryModel.model_fields.items()
            ]
            for year_month, entries in monthly_cashflows.items():
                if not ParserConfig.is_allowed_year_month(year_month):
                    continue

                monthly_file = self.parse_strategy.ensure_output_file_path(
                    f"{self.parse_strategy.account.name}({year_month}).csv")
                logger.info(f"Writing {len(entries)} entries to {monthly_file}")

                with open(monthly_file, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)

                    # Write the header row (id, name, price, is_available)
                    writer.writeheader()

                    # Write the rows
                    for entry in entries:
                        # .model_dump() converts the Pydantic object into a clean Python dict
                        writer.writerow(entry.model_dump(by_alias=True))

            logger.info(f"Successfully generated monthly reports from file `{file_path}`")
        except Exception as e:
            logger.exception(f"Error when processing file `{file_path}`: {e}")
