import time
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

class CorrelationEngine:
    def __init__(self, time_window_sec: float = 10.0, w_temporal: float = 0.6, w_network: float = 0.4):
        self.time_window_sec = time_window_sec
        self.w_temporal = w_temporal
        self.w_network = w_network

    def correlate(self, df: pd.DataFrame, time_window_sec: float = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        window = time_window_sec if time_window_sec is not None else self.time_window_sec
        start_time = time.time()

        if df.empty:
            return pd.DataFrame(), {"correlated_count": 0, "window_used": window}

        correlated_records = []

        # Convert timestamps to UTC pandas Datetime
        net_ts = pd.to_datetime(df["timestamp"], utc=True)
        tx_ts = pd.to_datetime(df["transaction_timestamp"], utc=True)

        # Calculate time delta in seconds
        deltas = np.abs((net_ts - tx_ts).dt.total_seconds())

        for idx, row in df.iterrows():
            delta = deltas.iloc[idx]
            if delta <= window:
                # Temporal score drops linearly with delta distance from transaction event
                temporal_score = max(0.0, 1.0 - (delta / window))
                
                # Network match score: 1.0 if valid IP/port present
                network_match_score = 1.0 if pd.notna(row.get("src_ip")) and row.get("src_ip") != "" else 0.5
                
                correlation_score = round(self.w_temporal * temporal_score + self.w_network * network_match_score, 4)

                corr_id = f"CORR_{idx+1:08d}"
                correlated_records.append({
                    "correlation_id": corr_id,
                    "txid": str(row["txid"]),
                    "src_ip": str(row["src_ip"]),
                    "input_wallet": str(row["input_wallet"]),
                    "output_wallet": str(row["output_wallet"]),
                    "net_timestamp": str(row["timestamp"]),
                    "tx_timestamp": str(row["transaction_timestamp"]),
                    "time_delta_sec": round(float(delta), 3),
                    "temporal_score": round(float(temporal_score), 4),
                    "network_match_score": round(float(network_match_score), 4),
                    "correlation_score": correlation_score
                })

        corr_df = pd.DataFrame(correlated_records)

        stats = {
            "total_transactions_analyzed": len(df),
            "correlated_candidates_found": len(corr_df),
            "time_window_sec_used": window,
            "avg_correlation_score": round(float(corr_df["correlation_score"].mean()), 4) if not corr_df.empty else 0.0,
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return corr_df, stats
