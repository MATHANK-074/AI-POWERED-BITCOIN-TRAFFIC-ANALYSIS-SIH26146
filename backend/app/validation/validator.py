import re
import ipaddress
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class DataValidator:
    def __init__(self, min_amount: float = 0.00000001, max_amount: float = 21000000.0, max_fee: float = 100.0):
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.max_fee = max_fee
        # Fast IPv4/IPv6 regex pattern
        self.ip_regex = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d)$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")

    def validate_and_clean(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        total_records = len(df)
        if total_records == 0:
            return pd.DataFrame(), pd.DataFrame(), {"records_received": 0, "records_valid": 0, "records_invalid": 0, "records_cleaned": 0, "records_removed": 0}

        # Work on a copy
        cleaned_df = df.copy()

        # Vectorized string cleanup
        for col in ["src_ip", "dst_ip", "txid", "input_wallet", "output_wallet"]:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()

        # 1. Required fields non-null check
        valid_mask = (
            cleaned_df["txid"].notna() & (cleaned_df["txid"] != "") &
            cleaned_df["timestamp"].notna() &
            cleaned_df["amount_btc"].notna()
        )

        # 2. Vectorized Numeric Amount & Fee checks
        cleaned_df["amount_btc"] = pd.to_numeric(cleaned_df["amount_btc"], errors="coerce")
        cleaned_df["fee_btc"] = pd.to_numeric(cleaned_df["fee_btc"], errors="coerce").fillna(0.0)

        valid_mask = valid_mask & (
            cleaned_df["amount_btc"].notna() &
            (cleaned_df["amount_btc"] >= 0) &
            (cleaned_df["amount_btc"] <= self.max_amount) &
            (cleaned_df["fee_btc"] >= 0) &
            (cleaned_df["fee_btc"] <= self.max_fee)
        )

        # 3. Vectorized Port range check
        cleaned_df["src_port"] = pd.to_numeric(cleaned_df["src_port"], errors="coerce")
        cleaned_df["dst_port"] = pd.to_numeric(cleaned_df["dst_port"], errors="coerce")
        
        valid_mask = valid_mask & (
            cleaned_df["src_port"].notna() & (cleaned_df["src_port"] >= 0) & (cleaned_df["src_port"] <= 65535) &
            cleaned_df["dst_port"].notna() & (cleaned_df["dst_port"] >= 0) & (cleaned_df["dst_port"] <= 65535)
        )

        # 4. Vectorized IP Validation
        src_ip_valid = cleaned_df["src_ip"].str.match(self.ip_regex, na=False)
        dst_ip_valid = cleaned_df["dst_ip"].str.match(self.ip_regex, na=False)
        valid_mask = valid_mask & src_ip_valid & dst_ip_valid

        # 5. Timestamp parsing
        cleaned_df["timestamp"] = pd.to_datetime(cleaned_df["timestamp"], errors="coerce", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        valid_mask = valid_mask & cleaned_df["timestamp"].notna()

        # Split into valid and rejected
        valid_df = cleaned_df[valid_mask].copy()
        rejected_df = cleaned_df[~valid_mask].copy()

        if not rejected_df.empty:
            rejected_df["rejection_reason"] = "Field validation failed (invalid IP, port, amount, or timestamp)"
            rejected_df["rejected_at"] = datetime.now(timezone.utc).isoformat() + "Z"

        stats = {
            "records_received": total_records,
            "records_valid": len(valid_df),
            "records_invalid": len(rejected_df),
            "records_cleaned": len(valid_df),
            "records_removed": len(rejected_df)
        }

        return valid_df, rejected_df, stats
