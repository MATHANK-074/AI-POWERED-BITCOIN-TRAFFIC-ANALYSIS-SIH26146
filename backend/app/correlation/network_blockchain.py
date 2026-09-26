import time
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from app.correlation.temporal import TemporalCorrelator
from app.correlation.matcher import MetadataMatcher
from app.config import CORRELATION_CFG

class NetworkBlockchainCorrelator:
    """
    Cross-Layer Network-Blockchain Correlation Engine.
    Correlates network metadata (IP, Port, Timestamp, ASN, Geo) with blockchain metadata
    (TXID, Wallet, Amount, Inputs, Outputs, Fee).
    Calculates multi-factor correlation confidence scores.

    DISCLAIMER: Network metadata and blockchain metadata are separate evidence sources that are correlated.
    IP addresses are NOT stored directly on the Bitcoin blockchain.
    """
    def __init__(self, time_window_sec: float = None, w_temporal: float = 0.6, w_network: float = 0.4):
        self.time_window_sec = time_window_sec or CORRELATION_CFG.get("default_time_window_sec", 10.0)
        self.w_temporal = w_temporal
        self.w_network = w_network
        self.temporal_correlator = TemporalCorrelator(default_window_sec=self.time_window_sec)
        self.metadata_matcher = MetadataMatcher()

    def correlate(self, df: pd.DataFrame, time_window_sec: float = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        window = time_window_sec or self.time_window_sec
        start_time = time.time()

        if df.empty:
            return pd.DataFrame(), {
                "total_transactions_analyzed": 0,
                "correlated_candidates_found": 0,
                "time_window_sec_used": window,
                "avg_correlation_score": 0.0,
                "processing_time_sec": 0.0
            }

        correlated_records = []

        # Vectorized calculation when both timestamp columns are present
        has_net_ts = "timestamp" in df.columns
        has_tx_ts = "transaction_timestamp" in df.columns

        for idx, row in df.iterrows():
            net_ts = str(row.get("timestamp", "")) if has_net_ts else ""
            tx_ts = str(row.get("transaction_timestamp", "")) if has_tx_ts else ""

            if not tx_ts and net_ts:
                tx_ts = net_ts

            temp_score, delta_sec = self.temporal_correlator.compute_temporal_score(net_ts, tx_ts, window_sec=window)
            meta_score = self.metadata_matcher.compute_metadata_score(row.to_dict())

            corr_score = round(self.w_temporal * temp_score + self.w_network * meta_score, 4)

            # Assign confidence classification
            if corr_score >= 0.8:
                conf = "HIGH"
            elif corr_score >= 0.5:
                conf = "MEDIUM"
            else:
                conf = "LOW"

            if temp_score > 0 or meta_score > 0.4:
                corr_id = f"CORR_{idx+1:08d}"
                correlated_records.append({
                    "correlation_id": corr_id,
                    "txid": str(row.get("txid", "")),
                    "src_ip": str(row.get("src_ip", "UNKNOWN")),
                    "dst_ip": str(row.get("dst_ip", "UNKNOWN")),
                    "input_wallet": str(row.get("input_wallet", "UNKNOWN")),
                    "output_wallet": str(row.get("output_wallet", "UNKNOWN")),
                    "net_timestamp": net_ts,
                    "tx_timestamp": tx_ts,
                    "time_delta_sec": delta_sec,
                    "temporal_score": temp_score,
                    "network_match_score": meta_score,
                    "correlation_score": corr_score,
                    "confidence_level": conf
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
