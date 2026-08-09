import sys
from pathlib import Path
from typing import Final
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from torch import Tensor

project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)
from src.enum.category import Category, CategoryInflow, CategoryOutflow
from src.enum.column import Column
from src.config.config import FileConfig
from src.utils.logger import logger, test_log


EMBEDDING_THRESHOLD: Final = 0.50  # similarity threshold for assigning category based on embedding similarity
EMBEDDING_CATEGORY_RESOLVER: Final = "embedding"


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

    def _build_reference_index(self) -> tuple[pd.DataFrame, np.ndarray]:
        """
        Load a labeled reference set and encode it.
        reference.csv must have columns: Details, Category
        """
        ref_data_dir = FileConfig.REFERENCE_DATA_DIR
        logger.info(f"Building reference index from files in {ref_data_dir}")

        reference_files = list(Path(ref_data_dir).glob("*.csv"))
        # FIXME: no guard for an empty/nonexistent reference directory — on a fresh checkout
        # (e.g. default .data/output with no CSVs yet), pd.concat([]) raises
        # `ValueError: No objects to concatenate`, crashing categorize() for a first-time user.
        reference_df = pd.concat([pd.read_csv(file) for file in reference_files], ignore_index=True)
        descriptions = reference_df[Column.DESCRIPTION.value].tolist()
        embeddings: np.ndarray = self.model.encode(descriptions, show_progress_bar=False)

        # TODO: save the reference embeddings to a file so that we don't have to re-encode every time

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

        df = df.copy()
        # uncategorized_mask = df[Column.CATEGORY.value].insna()
        uncategorized_mask = df[Column.CATEGORY.value] == ""
        uncategorized: pd.DataFrame = df[uncategorized_mask]

        if uncategorized.empty:
            logger.info("All rows categorized, no need to apply embedding")
            return df

        uncategorized_description_embeddings: np.ndarray = self.model.encode(
            uncategorized[Column.DESCRIPTION.value].tolist(),
            show_progress_bar=False,
        )

        # Computer the cosine similarity between each uncategorized entry and
        # all reference entries to resolve the category.
        # Given:
        # - uncategorized_description_embeddings has n elements,
        # - reference_embeddings has m elements,
        # Then:
        # - similarities has dimension: n (rows) * m (columns)
        similarities: Tensor = self.model.similarity(uncategorized_description_embeddings, reference_embeddings)
        # best_idx = similarities.argmax(axis=1)
        best_scores: Tensor  # highest similarities for each row
        best_indices: Tensor  # indices of the reference document for the highest similarity
        best_scores, best_indices = similarities.max(axis=1)

        for i, (original_idx, _) in enumerate(uncategorized.iterrows()):
            score: Tensor = best_scores[i]
            if score >= EMBEDDING_THRESHOLD:
                df.at[original_idx, Column.CATEGORY] = reference_df.iloc[best_indices[i].item()][Column.CATEGORY]
                df.at[original_idx, Column.CATEGORY_CONFIDENCE] = round(float(score), 4)
                df.at[original_idx, Column.CATEGORY_RESOLVER] = "embedding"

        # FIXME: dead variable, and semantically wrong — df is read with keep_default_na=False,
        # so no cell is ever NaN and .notna().sum() always equals len(df). The real "categorized
        # after embeddings" count using `!= ""` is already computed two lines below.
        categorized = df[Column.CATEGORY.value].notna().sum()
        total = len(df)
        logger.info(f"Categorized before embedding: {total - uncategorized_mask.sum()}/{total}\n" +
                    f"Categorized after embeddings: {(df[Column.CATEGORY.value] != "").sum()}/{total}")

        return df

    def get_output_csv_file_path(self, input_file_path: Path) -> Path:
        # FIXME: unconditionally appends ".csv" even when input_file_path already ends in .csv,
        # producing double extensions like "standardized_data_no_category.csv.csv".
        categorized_data_dir_path = Path(FileConfig.CATEGORIZED_DATA_DIR)
        categorized_data_dir_path.mkdir(parents=True, exist_ok=True)
        return Path(f"{categorized_data_dir_path}/{input_file_path.name}.csv")

    def categorize(self, file_path: Path) -> pd.DataFrame:
        """Categorize a transaction based on its details.
        This is only required when parse_strategy cannot determine the category."""

        if isinstance(file_path, str):
            file_path: Path = Path(file_path)

        if isinstance(file_path, Path):
            # NOTE: We need keep_default_na to false, since nan is considered a float,
            # leading to error with assigning str category
            df: pd.DataFrame = pd.read_csv(file_path, keep_default_na=False)
        else:
            raise TypeError(f"Input must be one of these types: str, Path. Actual: {type(file_path)}")

        # Categorize based on embedding similarity based on labeled data
        logger.info("Applying embedding similarity...")

        ref_df, ref_embeddings = self._build_reference_index()
        df = self._apply_embeddings(df, ref_df, ref_embeddings)

        # Write categorized result to file
        df.to_csv(self.get_output_csv_file_path(file_path),
                  index=False, encoding="utf-8", mode="w")

        return df
