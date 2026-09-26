import numpy as np
import pandas as pd
from typing import Dict, Any

class TransactionFeatureExtractor:
    """
    Extracts transaction-level forensic features: amount, fee, input/output counts, size, time features, percentiles.
    """
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        feat_df = df.copy()

        # Amount & Fee statistics
        amt = feat_df["amount_btc"].fillna(0.0) if "amount_btc" in feat_df.columns else pd.Series(0.0, index=df.index)
        fee = feat_df["fee_btc"].fillna(0.0) if "fee_btc" in feat_df.columns else pd.Series(0.0, index=df.index)

        feat_df["amount_btc"] = amt
        feat_df["fee_btc"] = fee
        feat_df["fee_ratio"] = (fee / (amt + 1e-8)).round(6)

        # Percentile features
        if len(amt) > 1:
            feat_df["amount_percentile"] = amt.rank(pct=True).round(4)
        else:
            feat_df["amount_percentile"] = 0.5

        # Inputs & Outputs counts and ratios
        in_cnt = feat_df["input_count"].fillna(1) if "input_count" in feat_df.columns else pd.Series(1, index=df.index)
        out_cnt = feat_df["output_count"].fillna(1) if "output_count" in feat_df.columns else pd.Series(1, index=df.index)

        feat_df["input_count"] = in_cnt
        feat_df["output_count"] = out_cnt
        feat_df["in_out_ratio"] = (in_cnt / (out_cnt + 1e-8)).round(4)

        return feat_df
