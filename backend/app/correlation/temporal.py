import numpy as np
import pandas as pd
from typing import Tuple

class TemporalCorrelator:
    """
    Computes temporal proximity score between network event timestamps and blockchain transaction timestamps.
    """
    def __init__(self, default_window_sec: float = 10.0):
        self.default_window_sec = default_window_sec

    def compute_temporal_score(self, net_timestamp: str, tx_timestamp: str, window_sec: float = None) -> Tuple[float, float]:
        window = window_sec or self.default_window_sec

        if not net_timestamp or not tx_timestamp:
            return 0.0, 999999.0

        try:
            t_net = pd.to_datetime(net_timestamp, utc=True)
            t_tx = pd.to_datetime(tx_timestamp, utc=True)
            delta_sec = abs((t_net - t_tx).total_seconds())

            if delta_sec <= window:
                # Score decays linearly from 1.0 (exact match) to 0.0 at window edge
                score = max(0.0, 1.0 - (delta_sec / window))
            else:
                score = 0.0

            return round(score, 4), round(delta_sec, 3)
        except Exception:
            return 0.0, 999999.0
