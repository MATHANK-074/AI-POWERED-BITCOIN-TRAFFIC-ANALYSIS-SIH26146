import time
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class FeatureEngine:
    def extract_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()

        if df.empty:
            return pd.DataFrame(), {"entity_count": 0}

        df = df.copy()
        df["tx_dt"] = pd.to_datetime(df["transaction_timestamp"], errors="coerce", utc=True)

        # 1. Input Wallets Aggregation (Outgoing transfers)
        in_agg = df.groupby("input_wallet").agg(
            out_degree=("txid", "count"),
            out_amount_sum=("amount_btc", "sum"),
            out_amount_avg=("amount_btc", "mean"),
            out_amount_max=("amount_btc", "max"),
            out_amount_min=("amount_btc", "min"),
            out_fee_avg=("fee_btc", "mean"),
            unique_ips=("src_ip", "nunique"),
            unique_ports=("src_port", "nunique"),
            out_counterparties=("output_wallet", "nunique")
        ).reset_index().rename(columns={"input_wallet": "entity_id"})

        # 2. Output Wallets Aggregation (Incoming transfers)
        out_agg = df.groupby("output_wallet").agg(
            in_degree=("txid", "count"),
            in_amount_sum=("amount_btc", "sum"),
            in_amount_avg=("amount_btc", "mean"),
            in_amount_max=("amount_btc", "max"),
            in_amount_min=("amount_btc", "min"),
            in_fee_avg=("fee_btc", "mean"),
            in_counterparties=("input_wallet", "nunique")
        ).reset_index().rename(columns={"output_wallet": "entity_id"})

        # Merge Wallet metrics
        wallet_df = pd.merge(in_agg, out_agg, on="entity_id", how="outer").fillna(0)
        wallet_df["entity_type"] = "wallet"
        
        wallet_df["tx_count"] = wallet_df["out_degree"] + wallet_df["in_degree"]
        wallet_df["total_amount_btc"] = np.round(wallet_df["out_amount_sum"] + wallet_df["in_amount_sum"], 8)
        wallet_df["avg_amount_btc"] = np.round(wallet_df["total_amount_btc"] / np.maximum(1, wallet_df["tx_count"]), 8)
        wallet_df["max_amount_btc"] = np.round(np.maximum(wallet_df["out_amount_max"], wallet_df["in_amount_max"]), 8)
        wallet_df["min_amount_btc"] = np.round(np.minimum(wallet_df["out_amount_min"], wallet_df["in_amount_min"]), 8)
        wallet_df["avg_fee_btc"] = np.round((wallet_df["out_fee_avg"] + wallet_df["in_fee_avg"]) / 2.0, 8)
        
        wallet_df["unique_ip_count"] = wallet_df["unique_ips"].astype(int)
        wallet_df["unique_port_count"] = wallet_df["unique_ports"].astype(int)
        wallet_df["unique_counterparties"] = (wallet_df["out_counterparties"] + wallet_df["in_counterparties"]).astype(int)
        wallet_df["in_degree"] = wallet_df["in_degree"].astype(int)
        wallet_df["out_degree"] = wallet_df["out_degree"].astype(int)
        wallet_df["in_out_ratio"] = np.round(wallet_df["in_degree"] / np.maximum(1, wallet_df["out_degree"]), 4)
        
        # Default burst & inter-tx times for vectorized wallet features
        wallet_df["burst_score"] = 0.0
        wallet_df["avg_inter_tx_time_sec"] = 0.0

        # Drop intermediate merge columns
        clean_cols = [
            "entity_id", "entity_type", "tx_count", "total_amount_btc", "avg_amount_btc",
            "max_amount_btc", "min_amount_btc", "avg_fee_btc", "unique_ip_count",
            "unique_port_count", "unique_counterparties", "in_degree", "out_degree",
            "in_out_ratio", "burst_score", "avg_inter_tx_time_sec"
        ]
        wallet_features = wallet_df[clean_cols]

        # 3. IP Aggregation
        ip_agg = df.groupby("src_ip").agg(
            tx_count=("txid", "count"),
            total_amount_btc=("amount_btc", "sum"),
            avg_amount_btc=("amount_btc", "mean"),
            max_amount_btc=("amount_btc", "max"),
            min_amount_btc=("amount_btc", "min"),
            avg_fee_btc=("fee_btc", "mean"),
            unique_ports=("src_port", "nunique"),
            unique_wallets=("input_wallet", "nunique")
        ).reset_index().rename(columns={"src_ip": "entity_id"})

        ip_agg["entity_type"] = "ip"
        ip_agg["total_amount_btc"] = np.round(ip_agg["total_amount_btc"], 8)
        ip_agg["avg_amount_btc"] = np.round(ip_agg["avg_amount_btc"], 8)
        ip_agg["max_amount_btc"] = np.round(ip_agg["max_amount_btc"], 8)
        ip_agg["min_amount_btc"] = np.round(ip_agg["min_amount_btc"], 8)
        ip_agg["avg_fee_btc"] = np.round(ip_agg["avg_fee_btc"], 8)
        ip_agg["unique_ip_count"] = 1
        ip_agg["unique_port_count"] = ip_agg["unique_ports"].astype(int)
        ip_agg["unique_counterparties"] = ip_agg["unique_wallets"].astype(int)
        ip_agg["in_degree"] = 0
        ip_agg["out_degree"] = ip_agg["tx_count"].astype(int)
        ip_agg["in_out_ratio"] = 1.0
        ip_agg["burst_score"] = 0.0
        ip_agg["avg_inter_tx_time_sec"] = 0.0

        ip_features = ip_agg[clean_cols]

        # Combine
        features_df = pd.concat([wallet_features, ip_features], ignore_index=True)

        stats = {
            "total_entities_extracted": len(features_df),
            "wallet_entities": len(wallet_features),
            "ip_entities": len(ip_features),
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return features_df, stats
