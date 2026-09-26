import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class NetworkFeatureExtractor:
    """
    Extracts aggregated behavioral features for IP network entities:
    connection count, unique ports, unique wallet counterparties, volume, burst activity.
    """
    def extract_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()

        if df.empty or "src_ip" not in df.columns:
            return pd.DataFrame(), {"total_ips_extracted": 0}

        ip_df = df[df["src_ip"].notna() & (df["src_ip"] != "") & (df["src_ip"] != "UNKNOWN")].copy()
        if ip_df.empty:
            return pd.DataFrame(), {"total_ips_extracted": 0}

        ip_records = []
        ip_df["ts"] = pd.to_datetime(ip_df["timestamp"], utc=True, errors="coerce")

        grouped = ip_df.groupby("src_ip")

        for ip, group in grouped:
            tx_count = len(group)
            amounts = group["amount_btc"].dropna()
            fees = group["fee_btc"].dropna()

            tot_amt = float(amounts.sum()) if not amounts.empty else 0.0
            avg_amt = float(amounts.mean()) if not amounts.empty else 0.0
            max_amt = float(amounts.max()) if not amounts.empty else 0.0
            min_amt = float(amounts.min()) if not amounts.empty else 0.0
            avg_fee = float(fees.mean()) if not fees.empty else 0.0

            unique_ports = int(group["src_port"].dropna().nunique()) if "src_port" in group.columns else 1
            unique_wallets = int(pd.concat([group["input_wallet"], group["output_wallet"]]).replace("UNKNOWN", np.nan).dropna().nunique())

            ts_sorted = group["ts"].dropna().sort_values()
            if len(ts_sorted) > 1:
                diffs = (ts_sorted.diff().dt.total_seconds()).dropna()
                avg_inter_tx = float(diffs.mean())
                burst_cnt = int((diffs <= 10.0).sum())
                burst_score = round(burst_cnt / len(diffs), 4)
            else:
                avg_inter_tx = 0.0
                burst_score = 0.0

            ip_records.append({
                "entity_id": str(ip),
                "entity_type": "ip",
                "tx_count": tx_count,
                "total_amount_btc": round(tot_amt, 8),
                "avg_amount_btc": round(avg_amt, 8),
                "max_amount_btc": round(max_amt, 8),
                "min_amount_btc": round(min_amt, 8),
                "avg_fee_btc": round(avg_fee, 8),
                "unique_ip_count": 1,
                "unique_port_count": unique_ports,
                "unique_counterparties": unique_wallets,
                "in_degree": 0,
                "out_degree": tx_count,
                "in_out_ratio": 0.0,
                "burst_score": burst_score,
                "avg_inter_tx_time_sec": round(avg_inter_tx, 2)
            })

        result_df = pd.DataFrame(ip_records)

        stats = {
            "total_ips_extracted": len(result_df),
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return result_df, stats
