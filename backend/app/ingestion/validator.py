import re
import time
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List

class DataValidator:
    """
    Data validator for Bitcoin forensic transactions and network metadata.
    Enforces required field presence, range checks, IP address validation,
    detects duplicates, logs missing fields, and tracks rejected records.
    """
    def __init__(self, min_amount: float = 0.0, max_amount: float = 21000000.0, max_fee: float = 100.0):
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.max_fee = max_fee
        # Regex pattern for IPv4 and IPv6
        self.ip_regex = re.compile(
            r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.){3}(25[0-5]|(2[0-4]|1\d|[1-9]|)\d)$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        )

    def validate(self, df: pd.DataFrame, source_file: str = "unknown", source_format: str = "CSV") -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        total_records = len(df)

        if total_records == 0:
            stats = {
                "filename": source_file,
                "format": source_format,
                "records_processed": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "duplicate_records": 0,
                "missing_fields": {},
                "processing_time_sec": 0.0
            }
            return pd.DataFrame(), pd.DataFrame(), stats

        work_df = df.copy()

        # Track missing values count per column
        missing_fields_count = {col: int(work_df[col].isna().sum()) for col in work_df.columns}

        # Check required fields
        has_txid = "txid" in work_df.columns
        has_amount = "amount_btc" in work_df.columns
        has_timestamp = "timestamp" in work_df.columns or "transaction_timestamp" in work_df.columns

        # Build rejection reasons array
        rejection_reasons = pd.Series([""] * total_records, index=work_df.index)
        is_valid = pd.Series([True] * total_records, index=work_df.index)

        # Rule 1: Required TXID or Identifier
        if has_txid:
            invalid_tx = work_df["txid"].isna() | (work_df["txid"] == "")
            is_valid = is_valid & (~invalid_tx)
            rejection_reasons[invalid_tx] += "Missing or empty TXID; "
        else:
            is_valid = pd.Series([False] * total_records, index=work_df.index)
            rejection_reasons += "Required TXID column missing; "

        # Rule 2: Numeric amount validation
        if has_amount:
            invalid_amt = work_df["amount_btc"].isna() | (work_df["amount_btc"] < self.min_amount) | (work_df["amount_btc"] > self.max_amount)
            is_valid = is_valid & (~invalid_amt)
            rejection_reasons[invalid_amt] += f"Invalid transaction amount (must be in [{self.min_amount}, {self.max_amount}]); "

        # Rule 3: Fee validation if fee present
        if "fee_btc" in work_df.columns:
            invalid_fee = work_df["fee_btc"].notna() & ((work_df["fee_btc"] < 0) | (work_df["fee_btc"] > self.max_fee))
            is_valid = is_valid & (~invalid_fee)
            rejection_reasons[invalid_fee] += f"Fee out of valid range [0, {self.max_fee}]; "

        # Rule 4: IP validation if present
        if "src_ip" in work_df.columns:
            ip_present = work_df["src_ip"].notna() & (work_df["src_ip"] != "")
            valid_ip_mask = work_df["src_ip"].astype(str).str.match(self.ip_regex, na=False)
            invalid_ip = ip_present & (~valid_ip_mask)
            is_valid = is_valid & (~invalid_ip)
            rejection_reasons[invalid_ip] += "Invalid source IP address format; "

        if "dst_ip" in work_df.columns:
            ip_present = work_df["dst_ip"].notna() & (work_df["dst_ip"] != "")
            valid_ip_mask = work_df["dst_ip"].astype(str).str.match(self.ip_regex, na=False)
            invalid_ip = ip_present & (~valid_ip_mask)
            is_valid = is_valid & (~invalid_ip)
            rejection_reasons[invalid_ip] += "Invalid destination IP address format; "

        # Rule 5: Port range check
        for p_col in ["src_port", "dst_port"]:
            if p_col in work_df.columns:
                port_vals = pd.to_numeric(work_df[p_col], errors="coerce")
                invalid_port = port_vals.notna() & ((port_vals < 0) | (port_vals > 65535))
                is_valid = is_valid & (~invalid_port)
                rejection_reasons[invalid_port] += f"Port {p_col} out of range [0, 65535]; "

        # Rule 6: Duplicate detection (by TXID if txid column present)
        duplicate_records_count = 0
        if has_txid:
            dups = work_df["txid"].duplicated(keep="first") & work_df["txid"].notna()
            duplicate_records_count = int(dups.sum())
            is_valid = is_valid & (~dups)
            rejection_reasons[dups] += "Duplicate TXID record; "

        # Split into valid and rejected records
        valid_df = work_df[is_valid].copy()
        rejected_df = work_df[~is_valid].copy()

        if not rejected_df.empty:
            rejected_df["rejection_reason"] = rejection_reasons[~is_valid].str.strip("; ")
            rejected_df["rejected_at"] = datetime.now(timezone.utc).isoformat()
            rejected_df["source_file"] = source_file

        processing_time = round(time.time() - start_time, 4)

        stats = {
            "filename": source_file,
            "format": source_format,
            "records_processed": total_records,
            "valid_records": len(valid_df),
            "invalid_records": len(rejected_df),
            "duplicate_records": duplicate_records_count,
            "missing_fields": missing_fields_count,
            "processing_time_sec": processing_time
        }

        return valid_df, rejected_df, stats
