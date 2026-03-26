import os
import pandas as pd
from pathlib import Path
from src.ingest.loader import DataLoader
from src.ingest.preprocessor import Preprocessor
from src.config.config import DATA_DIR, OUTPUT_DIR
from src.matchers.kb_mapper import KnowledgeBaseMatcher
from src.matchers.llm_matcher import LLMMatcher
from src.exporter.exporter import MappingExporter, ColumnMapper


class Pipeline:
    def __init__(self, file_name: str, file_dir: str = DATA_DIR):
        self.file_name = file_name
        self.file_stem = Path(file_name).stem
        self.file_path = os.path.join(file_dir, file_name)
        self.data_loader = DataLoader(self.file_path)
        self.preprocessor = Preprocessor(self.data_loader.load())

    def ingest(self) -> pd.DataFrame:
        df = self.data_loader.load()
        df = self.preprocessor.resolve_combined_columns(df)
        df.columns = self.preprocessor.preprocess_header(self.data_loader.get_columns())
        return df

    def key_mapping(self, df: pd.DataFrame) -> dict:
        matcher = KnowledgeBaseMatcher()
        return {col: matcher.match(col) for col in df.columns}

    def llm_mapping(self, mapping: dict) -> dict:
        return LLMMatcher().match(mapping)

    def export_mapping(self, mapping: dict, filename: str = None) -> Path:
        filename = filename or f"{self.file_stem}_mapping.json"
        return MappingExporter(OUTPUT_DIR).export(mapping, filename)

    def apply_mapping(self, df: pd.DataFrame, mapping: dict, filename: str = None) -> pd.DataFrame:
        filename = filename or f"{self.file_stem}_updated.csv"
        mapper = ColumnMapper(mapping, OUTPUT_DIR)
        df_mapped = mapper.apply(df)
        mapper.export_csv(df_mapped, filename=filename)
        return df_mapped


if __name__ == "__main__":
    pipeline = Pipeline("rfp_mixed_combined.csv")
    df = pipeline.ingest()
    kb_mapping = pipeline.key_mapping(df)
    final_mapping = pipeline.llm_mapping(kb_mapping)
    pipeline.export_mapping(final_mapping)
    pipeline.apply_mapping(df, final_mapping)

# input files
'''
rfp_complex.csv
rfp_currency_in_data.csv
rfp_descriptive.csv
rfp_mixed_combined.csv
rfp_shorthand.csv
rfp_standard.csv
'''