import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from app.ingestion.base_parser import BaseParser
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.validator import DataValidator

class XMLParser(BaseParser):
    """
    Safe XML parser for forensic transactions and event logs.
    """
    def __init__(self):
        self.normalizer = SchemaNormalizer()
        self.validator = DataValidator()

    def parse(self, file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        path = Path(file_path)
        filename = path.name

        tree = ET.parse(file_path)
        root = tree.getroot()

        records = []
        # Support common parent container tags: <records>, <transactions>, <dataset>, etc.
        for elem in root:
            record_dict = {}
            for child in elem:
                record_dict[child.tag] = child.text
            if record_dict:
                records.append(record_dict)

        df_raw = pd.DataFrame(records)
        mapped_df, _ = self.normalizer.map_columns(df_raw)
        norm_df = self.normalizer.normalize_fields(mapped_df)

        valid_df, rejected_df, stats = self.validator.validate(
            df=norm_df,
            source_file=filename,
            source_format="XML"
        )

        stats["total_raw_records"] = len(records)
        stats["ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()

        return valid_df, rejected_df, stats
