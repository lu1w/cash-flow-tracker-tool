import sys
from pathlib import Path
from typing import Final

import pandas as pd

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.config.config import FileConfig
from src.enum.column import Column
from src.enum.category_resolver import CategoryResolver
from src.utils.logger import logger

MANUAL_CATEGORY_RESOLVER: Final = "manual"
MANUAL_CATEGORY_CONFIDENCE: Final[int] = 1


def _get_standardized_path_from_category_reference_path(reference_file_path: Path) -> Path:
    reference_dir = Path(FileConfig.CATEGORY_REFERENCE_DATA_DIR)
    standardized_dir = Path(FileConfig.STANDARDIZED_DATA_DIR)

    try:
        relative_path = reference_file_path.relative_to(reference_dir)
    except ValueError:
        reference_path_str = str(reference_file_path)
        reference_dir_str = str(reference_dir)
        if reference_dir_str not in reference_path_str:
            raise ValueError(
                f"Reference file path must be under {reference_dir}: {reference_file_path}"
            )
        standardized_path_str = reference_path_str.replace(
            reference_dir_str, str(standardized_dir), 1
        )
        return Path(standardized_path_str)

    return standardized_dir / relative_path


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

    # reference_path = edited_file_path  # _cleansed_csv_path(file_path)
    # standardized_path = _to_standardized_path(reference_path)

    if verify_matching_suffix:
        if edited_file_path.name != original_file_path.name:
            raise ValueError(f"Mismatch suffix for files to compare")

    logger.info(
        f"Comparing edited categories in `{edited_file_path}` against original data in `{original_file_path}`"
    )

    original_df = pd.read_csv(original_file_path, keep_default_na=False)
    edited_df = pd.read_csv(edited_file_path, keep_default_na=False)

    original_categories = original_df.set_index(
        [Column.DATE, Column.AMOUNT_ABSOLUTE]
    )[Column.CATEGORY]

    manual_resolver_count = 0
    # edited_df = edited_df.copy()

    for idx, row in edited_df.iterrows():
        key = (row[Column.DATE], row[Column.AMOUNT_ABSOLUTE])

        if key not in original_categories.index:
            logger.error(f"Failed to find matching entry in standardized/ file for row key {key}")
            continue

        if row[Column.CATEGORY] != original_categories[key] and row[Column.CATEGORY] != CategoryResolver.MANUAL:
            edited_df.at[idx, Column.CATEGORY_RESOLVER] = MANUAL_CATEGORY_RESOLVER
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
            _get_standardized_path_from_category_reference_path(category_ref_file)
        )
        cleansed_df.to_csv(category_ref_file)


if __name__ == "__main__":
    cleanse_category_resolver()
