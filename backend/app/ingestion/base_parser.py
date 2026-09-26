from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Dict, Any

class BaseParser(ABC):
    """
    Abstract base class for chunked, format-agnostic data parsers.
    """
    @abstractmethod
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parses an input file and returns (DataFrame, metadata_dict).
        """
        pass
