import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
from app.ingestion.base_parser import BaseParser
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.validator import DataValidator

class JSONParser(BaseParser):
    """
    Parser for standard JSON arrays, nested JSON records, and line-delimited JSON (JSONL).
    """
    def __init__(self):
        self.normalizer = SchemaNormalizer()
        self.validator = DataValidator()

    def parse(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        path = Path(file_path)
        filename = path.name

        records = []
        # Attempt to read as JSONL first, then fallback to JSON array
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        record = json.loads(line_str)
                        if isinstance(record, dict):
                            records.append(record)
                    except json.JSONDecodeError:
                        break
        except Exception:
            pass

        if not records:
            # Fallback to standard JSON load
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    records = data.get("transactions") or data.get("records") or data.get("data") or [data]

        df_raw = pd.DataFrame(records)
        mapped_df, _ = self.normalizer.map_columns(df_raw)
        norm_df = self.normalizer.normalize_fields(mapped_df)

        valid_df, rejected_df, stats = self.validator.validate(
            df=norm_df,
            source_file=filename,
            source_format="JSON"
        )

        stats["total_raw_records"] = len(records)
        stats["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()

        return valid_df, rejected_df, stats
