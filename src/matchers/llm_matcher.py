from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from src.config.schema import TARGET_SCHEMA
from src.config.config import MODEL_NAME
import json
import re


PROMPT_TEMPLATE = """
You are an expert in international shipping and freight forwarding. Your task is to map non-standard RFP (Request for Proposal) column headers to a standardized internal schema.

**Target Schema:**
{target_schema}

**Input Columns:** {input_columns}

**Instructions:**
1. Analyze the input column names.
2. Determine which target schema fields they most likely represent.
3. Provide the reasoning for the mapping based on domain knowledge.
4. Provide the mapping in the following JSON format:
   {{
            "schema_field": "<field_name>",
            "input_field": "<input_column_name>",
            "confidence": <score_0_to_100>,
            "source": "llm",
            "status": "Match" if <score_0_to_100> >= 80 else "Verify",
            "reasoning": "<reasoning>",
   }}

**Scoring Guidelines:**
- 80-100: Direct match or very strong semantic similarity
- 60-79: Good match with some ambiguity
- 40-59: Possible match, requires context
- Below 40: Unlikely match, flag for manual review

**Examples:**
Input: "40HQ Rate" -> {{    "schema_field": "container_type_40hq_rate", "input_field": "40HQ Rate", "confidence": 92,"source": "llm", "status": "Match", "reasoning": "Direct match"}}
Input: "Transit (days)" -> {{"schema_field": "transit_time_days", "input_field": "Transit (days)", "confidence": 88, "source": "llm", "status": "Match", "reasoning": "Direct match"}}

Now, map ONLY these columns and return a JSON array: {input_columns}
"""


class LLMMatcher:
    def __init__(self, target_schema: list = TARGET_SCHEMA, model: str = MODEL_NAME):
        self.target_schema = target_schema
        self.llm = ChatOpenAI(model=model)
        self.llm_chain = PromptTemplate(
            input_variables=["target_schema", "input_columns"],
            template=PROMPT_TEMPLATE
        ) | self.llm

    def match(self, kb_mapping: dict) -> dict:
        verify_columns = [
            field for field, result in kb_mapping.items()
            if result["status"] == "Verify"
        ]

        if not verify_columns:
            return kb_mapping

        result = self.llm_chain.invoke({
            "target_schema": "\n".join(f"- {field}" for field in self.target_schema),
            "input_columns": ", ".join(verify_columns),
        })

        llm_results = self._parse(result.content, verify_columns)
        return {**kb_mapping, **llm_results}

    # def _parse(self, content: str, verify_columns: list) -> dict:
    #     raw = re.sub(r"```json|```", "", content).strip()
    #     parsed = json.loads(raw)
  
    #     if "schema_field" in parsed:
    #         input_field = parsed.get("input_field")
    #         parsed = {input_field: parsed}

    #     return parsed

    # def _parse(self, content: str, verify_columns: list) -> dict:
    #     raw = re.sub(r"```json|```", "", content).strip()

    #     if not raw:
    #         print(f"[LLMMatcher] Warning: empty response from LLM.")
    #         return {}

    #     try:
    #         parsed = json.loads(raw)
    #     except json.JSONDecodeError as e:
    #         print(f"[LLMMatcher] JSONDecodeError: {e}\nRaw:\n{raw}")
    #         return {}

    #     if isinstance(parsed, list):
    #         parsed = {
    #             item.get("input_field", verify_columns[i]): item
    #             for i, item in enumerate(parsed)
    #         }

    #     elif "schema_field" in parsed:
    #         input_field = parsed.get("input_field", verify_columns[0])
    #         parsed = {input_field: parsed}

    #     return parsed
    def _parse(self, content: str, verify_columns: list) -> dict:
        if not content or not content.strip():
            print("[LLMMatcher] Warning: empty response from LLM.")
            return {}

        # ── Strategy 1: strip markdown fences and try direct JSON parse ──
        raw = re.sub(r"```json|```", "", content).strip()

        try:
            parsed = json.loads(raw)
            return self._normalize(parsed, verify_columns)
        except json.JSONDecodeError:
            pass

        # ── Strategy 2: extract all {...} blocks via regex (handles prose + JSON mix) ──
        json_blocks = re.findall(r'\{[^{}]+\}', content, re.DOTALL)

        if json_blocks:
            items = []
            seen_keys = set()  # guard against duplicate keys inside a single block

            for block in json_blocks:
                # Remove duplicate keys that the LLM sometimes emits
                block = self._deduplicate_keys(block)
                try:
                    parsed_block = json.loads(block)
                    if "schema_field" in parsed_block and "input_field" in parsed_block:
                        items.append(parsed_block)
                except json.JSONDecodeError:
                    continue

            if items:
                return self._normalize(items, verify_columns)

        print(f"[LLMMatcher] Warning: could not parse LLM response.\nRaw:\n{content}")
        return {}

    def _normalize(self, parsed, verify_columns: list) -> dict:
        """Convert parsed JSON (list or single dict) to {input_field: mapping} dict."""
        if isinstance(parsed, list):
            return {
                item.get("input_field", verify_columns[i]): item
                for i, item in enumerate(parsed)
                if isinstance(item, dict)
            }
        if isinstance(parsed, dict) and "schema_field" in parsed:
            input_field = parsed.get("input_field", verify_columns[0])
            return {input_field: parsed}
        return {}

    @staticmethod
    def _deduplicate_keys(block: str) -> str:
        """Remove duplicate key lines the LLM sometimes emits inside a JSON block."""
        seen, clean_lines = set(), []
        for line in block.splitlines():
            key_match = re.match(r'\s*"(\w+)"\s*:', line)
            if key_match:
                key = key_match.group(1)
                if key in seen:
                    continue
                seen.add(key)
            clean_lines.append(line)
        return "\n".join(clean_lines)

