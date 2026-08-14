import sys
from pathlib import Path
from typing import Final, Iterable
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from torch import Tensor

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.account import Account, ALL_ACTIVE_ACCOUNTS
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.category_resolver import CategoryResolver
from src.enum.column import Column
from src.config.config import FileConfig
from src.utils.file_paths_utils import map_file_path
from src.utils.logger import logger, debug_log


EMBEDDING_THRESHOLD: Final = 0.50


class ReferenceEntry(BaseModel):
    # TODO: utilize pydantic library to create a typed model for reference_csv entries
    description: str
    category: Category


class Categorizer():
    # Qwen model has 4B and 8B versions, but 0.6B is faster and uses less memory
    def __init__(self, sentence_transformer_model_name: str = "Qwen/Qwen3-Embedding-0.6B"):
        # Recommended on Hugging Face https://huggingface.co/Qwen/Qwen3-Embedding-8B:
        # Enabling flash_attention_2 for better acceleration and memory saving,
        # together with setting `padding_side` to "left":
        self.model = SentenceTransformer(
            sentence_transformer_model_name,
            # model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
            # tokenizer_kwargs={"padding_side": "left"},
        )

    def _build_category_reference_index(self, account_dir_name: str) -> tuple[pd.DataFrame, np.ndarray]:
        """
        Load a labeled reference set in a CSV and encode it.
        The reference CSV must have columns: Description, Category
        """
        ref_data_dir = Path(FileConfig.CATEGORY_REFERENCE_DATA_DIR) / account_dir_name
        reference_files = list(ref_data_dir.glob("*.csv"))
        logger.info(f"Building reference index from {len(reference_files)} files in {ref_data_dir}")

        reference_df = pd.concat([pd.read_csv(file) for file in reference_files], ignore_index=True)
        descriptions = reference_df[Column.DESCRIPTION.value].tolist()
        embeddings: np.ndarray = self.model.encode(descriptions, show_progress_bar=False)

        return reference_df, embeddings

    def _apply_embeddings(
        self,
        df: pd.DataFrame,
        reference_df: pd.DataFrame,
        reference_embeddings: np.ndarray | Tensor,
    ) -> pd.DataFrame:
        """
        For uncategorized rows, find the most similar reference entry.
        If similarity >= threshold, assign its category.
        """
        logger.info("Resolve category based on cosine similarties...")

        def get_uncategorized_mask(df: pd.DataFrame) -> pd.Series:
            return (
                (df[Column.CATEGORY.value] == "Unknown")
                # the following two cases should not happen, just for extra safety
                | (df[Column.CATEGORY.value] == "")
                | df[Column.CATEGORY.value].isna()
            )

        df = df.copy()
        uncategorized_mask: pd.Series[bool] = get_uncategorized_mask(df)
        uncategorized: pd.DataFrame = df[uncategorized_mask]

        if uncategorized.empty:
            logger.info("All rows categorized, no need to apply embedding")
            return df

        uncategorized_description_embeddings: np.ndarray = self.model.encode(
            uncategorized[Column.DESCRIPTION.value].tolist(),
            show_progress_bar=False,
        )

        # Compute the cosine similarity between each uncategorized entry and
        # all reference entries to resolve the category.
        # Given:
        # - uncategorized_description_embeddings has n elements,
        # - reference_embeddings has m elements,
        # Then:
        # - similarities has dimension: n (rows) * m (columns)
        similarities: Tensor = self.model.similarity(uncategorized_description_embeddings, reference_embeddings)

        best_scores: Tensor  # highest similarities for each row
        best_indices: Tensor  # indices of the reference document for the highest similarity
        best_scores, best_indices = similarities.max(axis=1)

        for i, (original_idx, _) in enumerate(uncategorized.iterrows()):
            score: Tensor = best_scores[i]
            if score >= EMBEDDING_THRESHOLD:
                df.at[original_idx, Column.CATEGORY] = reference_df.iloc[best_indices[i].item()][Column.CATEGORY]
                df.at[original_idx, Column.CATEGORY_CONFIDENCE] = round(float(score), 4)
                df.at[original_idx, Column.CATEGORY_RESOLVER] = CategoryResolver.EMBEDDING

        total = len(df)
        logger.info(f"Categorized before embedding: {total - uncategorized_mask.sum()}/{total}\n" +
                    f"Categorized after embeddings: {(~get_uncategorized_mask(df)).sum()}/{total}")

        return df

    def _map_standardized_file_to_categorized_file(self, standardized_file: Path) -> Path:
        categorized_file = map_file_path(
            standardized_file,
            FileConfig.STANDARDIZED_DATA_DIR,
            FileConfig.CATEGORIZED_DATA_DIR)
        return categorized_file

    def categorize_file(self, file_path: Path | str, ref_df: pd.DataFrame, ref_embeddings) -> pd.DataFrame:
        """
        Reads reference data, and matches the description of uncategorized entries to the
        reference data based on embedding similarity to categorize the uncategorized entries.

        :param file_path: Path to the standardized data CSV file to be categorized. E.g. .data/standardized/.alipay/ALIPAY(202602).csv
        """
        if isinstance(file_path, str):
            file_path: Path = Path(file_path)

        if isinstance(file_path, Path):
            # NOTE: We need keep_default_na to false, since nan is considered a float,
            # leading to error with assigning str typed category
            df: pd.DataFrame = pd.read_csv(file_path, keep_default_na=False)
        else:
            raise TypeError(f"Input must be one of these types: str, Path. Actual: {type(file_path)}")

        # Categorize based on embedding similarity based on labeled data
        logger.info(f"Applying embedding similarity to {file_path}...")

        df = self._apply_embeddings(df, ref_df, ref_embeddings)

        # Write categorized result to file
        categorized_file = self._map_standardized_file_to_categorized_file(file_path)
        categorized_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(categorized_file, index=False, encoding="utf-8", mode="w")

        return df

    def categorize_all_standardized_files(
        self,
        standardized_file_dir: str = FileConfig.STANDARDIZED_DATA_DIR,
        accounts: Iterable[Account | str] = ALL_ACTIVE_ACCOUNTS
    ) -> None:
        for account in accounts:
            ref_df, ref_embeddings = self._build_category_reference_index(account.dir_name)
            # TODO(CG3): save the reference embeddings to a file so that we don't have to re-encode every time

            standardized_dir = Path(standardized_file_dir) / account.dir_name
            standardized_files = standardized_dir.rglob("*.csv")
            for standardized_file in standardized_files:
                self.categorize_file(standardized_file, ref_df, ref_embeddings)
