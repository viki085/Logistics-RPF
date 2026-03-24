import os
import argparse
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

    def run(self) -> None:
        print(f"\n[Pipeline] Processing: {self.file_name}")
        df = self.ingest()
        kb_mapping = self.key_mapping(df)
        final_mapping = self.llm_mapping(kb_mapping)
        self.export_mapping(final_mapping)
        self.apply_mapping(df, final_mapping)
        print(f"[Pipeline] Done: {self.file_name}")


def run_batch(input_dir: str, extension: str = ".csv") -> None:
    files = [f for f in os.listdir(input_dir) if f.endswith(extension)]

    if not files:
        print(f"[Batch] No {extension} files found in: {input_dir}")
        return

    print(f"[Batch] Found {len(files)} file(s) in: {input_dir}")

    failed = []
    for file_name in files:
        try:
            Pipeline(file_name, file_dir=input_dir).run()
        except Exception as e:
            print(f"[Batch] Failed: {file_name} — {e}")
            failed.append(file_name)

    print(f"\n[Batch] Complete — {len(files) - len(failed)}/{len(files)} succeeded")
    if failed:
        print(f"[Batch] Failed: {failed}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Path to folder containing input CSV files")
    args = parser.parse_args()

    run_batch(args.input_dir)

