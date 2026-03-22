import json
from pathlib import Path
import pandas as pd
from src.config.config import OUTPUT_DIR



class MappingExporter:
    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, mapping: dict, filename: str = "mapping_results.json") -> Path:
        structured = {
            "summary": {
                "total":   len(mapping),
                "matched": sum(1 for r in mapping.values() if r["status"] == "Match"),
                "verify":  sum(1 for r in mapping.values() if r["status"] == "Verify"),
                "kb_resolved":  sum(1 for r in mapping.values() if r["source"] == "kb"),
                "llm_resolved": sum(1 for r in mapping.values() if r["source"] == "llm"),
            },
            "mappings": mapping
        }

        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(structured, f, indent=4)

        # return output_path

class ColumnMapper:
    def __init__(self, mapping: dict, output_dir: str = OUTPUT_DIR):
        self.mapping = mapping.get("mappings", mapping)
        self.output_dir = Path(output_dir)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        rename_map = {
            result["input_field"]: result["schema_field"]
            for result in self.mapping.values()
            if result["status"] == "Match"
        }

        unmapped = [col for col in df.columns if col not in rename_map]
        if unmapped:
            print(f"Warning: no mapping found for columns: {unmapped}")

        return df.rename(columns=rename_map)

    def export_csv(self, df: pd.DataFrame, filename: str = "updated_data.csv") -> Path:
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        # return output_path