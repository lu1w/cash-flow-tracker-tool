import sys
from pathlib import Path
from typing import Final

import pandas as pd

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import FileConfig
from src.enum.column import Column
from src.enum.category_resolver import CategoryResolver
from src.utils.file_paths_utils import map_file_path
from src.utils.logger import logger

MANUAL_CATEGORY_CONFIDENCE: Final[int] = 1


def _map_category_reference_file_to_standardized_file(reference_file_path: Path) -> Path:
    return map_file_path(reference_file_path, FileConfig.CATEGORY_REFERENCE_DATA_DIR, FileConfig.STANDARDIZED_DATA_DIR)


def _mark_manual_category_resolver(
    edited_file_path: Path | str,
    original_file_path: Path | str,
    verify_matching_suffix: bool = True
) -> pd.DataFrame:
    """
    Compare categories in a human-edited CSV against the matching non-human-edited CSV.

    For rows where the human-edited category differs from the non-human-edited category,
    mark "Category Resolver" column as "manual" and "Category Confidence" column as 1.

    :param edited_file_path: Path to the human-edited version CSV, e.g. .data/reference/alipay/ALIPAY(2025-06)
    :param original_file_path: Path to the non-edited version CSV, e.g. .data/standardized/alipay/ALIPAY(2025-06)
    :param verify_matching_suffix: Whether to throw an exception if suffix of the `edited_file_path` and `original_file_path` doesn't match
    :return: Updated human-edited DataFrame
    """
    # TODO(PL14): make the cleanser generic, to cover all cases where human can edit the category

    if isinstance(edited_file_path, str):
        edited_file_path = Path(edited_file_path)
    if isinstance(original_file_path, str):
        original_file_path = Path(original_file_path)

    if verify_matching_suffix:
        if edited_file_path.name != original_file_path.name:
            raise ValueError(f"Mismatch suffix for files to compare")

    logger.info(
        f"Comparing edited categories in `{edited_file_path}` against original data in `{original_file_path}`"
    )

    original_df = pd.read_csv(original_file_path, keep_default_na=False)
    edited_df = pd.read_csv(edited_file_path, keep_default_na=False)

    manual_resolver_count = 0
    # edited_df = edited_df.copy()

    for idx, row in edited_df.iterrows():
        if (
            row[Column.CATEGORY] != original_df.at[idx, Column.CATEGORY]
            or row[Column.DESCRIPTION] != original_df.at[idx, Column.DESCRIPTION]
        ):
            if ((row[Column.DATE], row[Column.AMOUNT_ABSOLUTE])
                    != (original_df.at[idx, Column.DATE], original_df.at[idx, Column.AMOUNT_ABSOLUTE])):
                logger.error(
                    f"Row edited by human does not have the same keyed row in the original file at the same index {idx}.\n"
                    + f"Edited row: date={row[Column.DATE]}, amount={row[Column.AMOUNT_ABSOLUTE]};\n"
                    + f"original row: date={original_df.at[idx, Column.DATE]}, amount={original_df.at[idx, Column.AMOUNT_ABSOLUTE]}.")
                continue

            edited_df.at[idx, Column.CATEGORY_RESOLVER] = CategoryResolver.MANUAL
            edited_df.at[idx, Column.CATEGORY_CONFIDENCE] = int(MANUAL_CATEGORY_CONFIDENCE)
            manual_resolver_count += 1

    logger.info(
        f"Marked {manual_resolver_count}/{len(edited_df)} rows as manually resolved categories"
    )

    return edited_df


def cleanse_category_resolver() -> None:
    """
    Compare categories in a reference CSV against the matching standardized CSV.

    For rows where the reference category differs from the standardized category,
    mark "Category Resolver" column as "manual" and "Category Confidence" column as 1.
    """
    category_reference_dir = Path(FileConfig.CATEGORY_REFERENCE_DATA_DIR)
    category_reference_files = sorted(category_reference_dir.rglob("*.csv"))

    if len(category_reference_files) <= 0:
        logger.warning(f"No files found in {category_reference_dir}")
        return

    logger.info(
        f"Running category resolver cleanse on {len(category_reference_files)} file(s) in `{category_reference_files}`"
    )

    for category_ref_file in category_reference_files:
        cleansed_df = _mark_manual_category_resolver(
            category_ref_file,
            _map_category_reference_file_to_standardized_file(category_ref_file)
        )
        cleansed_df.to_csv(category_ref_file, index=False, encoding="utf-8")


if __name__ == "__main__":
    cleanse_category_resolver()
