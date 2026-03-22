import os
import pandas as pd
from thefuzz import fuzz
from src.config.schema import TARGET_SCHEMA, FIELD_KNOWLEDGE_BASE
from src.ingest.preprocessor import Preprocessor


class KnowledgeBaseMatcher:
    def __init__(self, knowledge_base: dict = FIELD_KNOWLEDGE_BASE, threshold: int = 75):
        self.knowledge_base = knowledge_base
        self.threshold = threshold

    def match(self, input_field: str) -> list:
        results = []

        for schema_field, synonyms in self.knowledge_base.items():
            best_score = 0

            for synonym in synonyms:
                if input_field == synonym:
                    best_score = 100
                    break
                best_score = max(best_score, fuzz.ratio(input_field, synonym))

            if best_score >= self.threshold:
                results.append({
                    "schema_field":schema_field,
                    "input_field":input_field,
                    "confidence":best_score,
                    "source":"kb",
                    "status":"Match" if best_score == 100 else "Verify",
                })

        if not results:
            results.append({
                "schema_field":"Unknown",
                "input_field":input_field,
                "confidence":0,
                "source":"kb",
                "status":"Verify",
            })

        return max(results, key=lambda x: x["confidence"])