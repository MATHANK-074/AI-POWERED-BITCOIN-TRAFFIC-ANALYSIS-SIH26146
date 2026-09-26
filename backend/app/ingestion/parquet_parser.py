import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
from app.ingestion.base_parser import BaseParser
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.validator import DataValidator

class ParquetParser(BaseParser):
    """
    Parser for Parquet datasets supporting chunked processing and schema mapping.
    """
    def __init__(self):
        self.normalizer = SchemaNormalizer()
        self.validator = DataValidator()

    def parse(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        path = Path(file_path)
        filename = path.name

        try:
            import pyarrow.parquet as pq
            parquet_file = pq.ParquetFile(file_path)
            chunks = []
            total_raw_rows = 0

            for batch in parquet_file.iter_batches(batch_size=50000):
                chunk_df = batch.to_pandas()
                mapped_chunk, _ = self.normalizer.map_columns(chunk_df)
                norm_chunk = self.normalizer.normalize_fields(mapped_chunk)
                chunks.append(norm_chunk)
                total_raw_rows += len(norm_chunk)

            if chunks:
                combined_df = pd.concat(chunks, ignore_index=True)
            else:
                combined_df = pd.DataFrame()

        except Exception:
            # Fallback to direct pandas read_parquet
            df_raw = pd.read_parquet(file_path)
            total_raw_rows = len(df_raw)
            mapped_df, _ = self.normalizer.map_columns(df_raw)
            combined_df = self.normalizer.normalize_fields(mapped_df)

        valid_df, rejected_df, stats = self.validator.validate(
            df=combined_df,
            source_file=filename,
            source_format="Parquet"
        )

        stats["total_raw_records"] = total_raw_rows
        stats["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
        stats["processing_time_sec"] = round(time.time() - start_time, 4)

        return valid_df, rejected_df, stats
