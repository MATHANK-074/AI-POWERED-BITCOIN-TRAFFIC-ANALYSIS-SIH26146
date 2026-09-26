import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
from app.ingestion.base_parser import BaseParser
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.validator import DataValidator

class CSVParser(BaseParser):
    """
    Chunked CSV parser supporting multi-gigabyte files with automatic schema mapping.
    """
    def __init__(self, chunksize: int = 50000):
        self.chunksize = chunksize
        self.normalizer = SchemaNormalizer()
        self.validator = DataValidator()

    def parse(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        path = Path(file_path)
        filename = path.name

        chunks = []
        total_raw_rows = 0

        # Read CSV in memory-safe chunks
        for chunk in pd.read_csv(file_path, chunksize=self.chunksize, low_memory=False):
            mapped_chunk, _ = self.normalizer.map_columns(chunk)
            norm_chunk = self.normalizer.normalize_fields(mapped_chunk)
            chunks.append(norm_chunk)
            total_raw_rows += len(norm_chunk)

        if chunks:
            combined_df = pd.concat(chunks, ignore_index=True)
        else:
            combined_df = pd.DataFrame()

        valid_df, rejected_df, stats = self.validator.validate(
            df=combined_df,
            source_file=filename,
            source_format="CSV"
        )

        stats["total_raw_records"] = total_raw_rows
        stats["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()

        return valid_df, rejected_df, stats
