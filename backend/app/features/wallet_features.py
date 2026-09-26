import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class WalletFeatureExtractor:
    """
    Extracts aggregated behavioral features for Bitcoin wallet entities:
    total volume, transaction count, avg/max/min amount, avg fee, unique counterparties,
    fan-in, fan-out, burst score, and inter-transaction time.
    """
    def extract_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()

        if df.empty:
            return pd.DataFrame(), {"total_wallets_extracted": 0}

        wallet_records = []

        # Parse timestamps for inter-tx calculation
        work_df = df.copy()
        work_df["ts"] = pd.to_datetime(work_df["timestamp"], utc=True, errors="coerce")

        # Gather all unique wallets across input_wallet and output_wallet
        inputs = work_df[["input_wallet", "amount_btc", "fee_btc", "src_ip", "dst_wallet", "output_wallet", "ts"]].rename(
            columns={"input_wallet": "wallet", "output_wallet": "counterparty", "dst_wallet": "counterparty2"}
        )
        inputs["direction"] = "outflow"

        outputs = work_df[["output_wallet", "amount_btc", "fee_btc", "src_ip", "input_wallet", "ts"]].rename(
            columns={"output_wallet": "wallet", "input_wallet": "counterparty"}
        )
        outputs["direction"] = "inflow"

        combined = pd.concat([inputs, outputs], ignore_index=True)
        combined = combined[combined["wallet"].notna() & (combined["wallet"] != "") & (combined["wallet"] != "UNKNOWN")]

        grouped = combined.groupby("wallet")

        for wallet, group in grouped:
            tx_count = len(group)
            amounts = group["amount_btc"].dropna()
            fees = group["fee_btc"].dropna()

            tot_amt = float(amounts.sum()) if not amounts.empty else 0.0
            avg_amt = float(amounts.mean()) if not amounts.empty else 0.0
            max_amt = float(amounts.max()) if not amounts.empty else 0.0
            min_amt = float(amounts.min()) if not amounts.empty else 0.0
            avg_fee = float(fees.mean()) if not fees.empty else 0.0

            unique_ips = int(group["src_ip"].replace("UNKNOWN", np.nan).dropna().nunique())
            counterparties = int(group["counterparty"].replace("UNKNOWN", np.nan).dropna().nunique())

            in_deg = int((group["direction"] == "inflow").sum())
            out_deg = int((group["direction"] == "outflow").sum())
            ratio = round(in_deg / max(1, out_deg), 4)

            # Compute rapid burst activity & inter-tx times
            ts_sorted = group["ts"].dropna().sort_values()
            if len(ts_sorted) > 1:
                diffs = (ts_sorted.diff().dt.total_seconds()).dropna()
                avg_inter_tx = float(diffs.mean())
                burst_cnt = int((diffs <= 10.0).sum())
                burst_score = round(burst_cnt / len(diffs), 4)
            else:
                avg_inter_tx = 0.0
                burst_score = 0.0

            wallet_records.append({
                "entity_id": str(wallet),
                "entity_type": "wallet",
                "tx_count": tx_count,
                "total_amount_btc": round(tot_amt, 8),
                "avg_amount_btc": round(avg_amt, 8),
                "max_amount_btc": round(max_amt, 8),
                "min_amount_btc": round(min_amt, 8),
                "avg_fee_btc": round(avg_fee, 8),
                "unique_ip_count": unique_ips,
                "unique_port_count": 1,
                "unique_counterparties": counterparties,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "in_out_ratio": ratio,
                "burst_score": burst_score,
                "avg_inter_tx_time_sec": round(avg_inter_tx, 2)
            })

        wallet_df = pd.DataFrame(wallet_records)

        stats = {
            "total_wallets_extracted": len(wallet_df),
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return wallet_df, stats
