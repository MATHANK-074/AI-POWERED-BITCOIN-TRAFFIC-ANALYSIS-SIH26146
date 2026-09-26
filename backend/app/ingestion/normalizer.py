import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

# Configurable schema mapping definitions for heterogeneous datasets
SCHEMA_MAP = {
    "txid": ["txid", "transaction_id", "hash", "tx_hash", "tx_id", "tx_identifier"],
    "timestamp": ["timestamp", "time", "datetime", "tx_time", "net_timestamp", "block_time", "date"],
    "src_ip": ["src_ip", "source_ip", "ip_src", "src", "client_ip", "sender_ip", "origin_ip"],
    "dst_ip": ["dst_ip", "destination_ip", "ip_dst", "dst", "server_ip", "receiver_ip", "target_ip"],
    "src_port": ["src_port", "source_port", "port_src", "sport"],
    "dst_port": ["dst_port", "destination_port", "port_dst", "dport"],
    "input_wallet": ["input_wallet", "src_wallet", "sender_wallet", "from_address", "input_address", "src_address", "vin_address", "wallet", "address", "bitcoin_address"],
    "output_wallet": ["output_wallet", "dst_wallet", "receiver_wallet", "to_address", "output_address", "dst_address", "vout_address"],
    "amount_btc": ["amount_btc", "amount", "value", "value_btc", "btc_amount", "sum_btc"],
    "fee_btc": ["fee_btc", "fee", "miner_fee", "tx_fee", "fee_satoshis"],
    "protocol": ["protocol", "net_protocol", "p2p_protocol"],
    "network_event_id": ["network_event_id", "event_id", "net_id"],
    "transaction_timestamp": ["transaction_timestamp", "block_timestamp", "tx_datetime", "blockchain_time"],
    "input_count": ["input_count", "vin_count", "num_inputs", "in_count"],
    "output_count": ["output_count", "vout_count", "num_outputs", "out_count"],
    "transaction_size": ["transaction_size", "size_bytes", "vsize", "tx_size"],
    "block_height": ["block_height", "block_number", "height", "block_no"],
    "asn": ["asn", "bgp_asn", "autonomous_system"],
    "country": ["country", "country_code", "geo_country"],
    "city": ["city", "geo_city"],
    "synthetic_entity_id": ["synthetic_entity_id", "entity_id", "ground_truth_entity"],
    "synthetic_behavior_type": ["synthetic_behavior_type", "behavior", "behavior_type"],
    "synthetic_pattern_label": ["synthetic_pattern_label", "pattern_label", "label", "class"]
}

class SchemaNormalizer:
    """
    Normalizes heterogeneous dataframe column names into standard KRISHIGUARD schema fields,
    normalizes data types, formats timestamps to ISO UTC, and cleans string identifiers.
    """
    def __init__(self, custom_mapping: Dict[str, List[str]] = None):
        self.mapping = custom_mapping if custom_mapping else SCHEMA_MAP

    def map_columns(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Maps input dataframe column headers to target schema names.
        """
        renamed_cols = {}
        matched_targets = set()

        # Lowercase mapping for case-insensitive matching
        col_lower_map = {c.lower().strip(): c for c in df.columns}

        for target_field, aliases in self.mapping.items():
            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in col_lower_map and target_field not in matched_targets:
                    orig_col = col_lower_map[alias_lower]
                    renamed_cols[orig_col] = target_field
                    matched_targets.add(target_field)
                    break

        mapped_df = df.rename(columns=renamed_cols).copy()
        return mapped_df, renamed_cols

    def normalize_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes individual field values according to target data types.
        """
        if df.empty:
            return df

        norm_df = df.copy()

        # Clean string IDs
        for str_col in ["txid", "src_ip", "dst_ip", "input_wallet", "output_wallet", "protocol", "country", "city"]:
            if str_col in norm_df.columns:
                norm_df[str_col] = norm_df[str_col].astype(str).str.strip()
                norm_df[str_col] = norm_df[str_col].replace(["nan", "None", "null", "NaN", ""], np.nan)

        # Standardize numeric values
        for num_col in ["amount_btc", "fee_btc", "src_lat", "src_lon", "dst_lat", "dst_lon"]:
            if num_col in norm_df.columns:
                norm_df[num_col] = pd.to_numeric(norm_df[num_col], errors="coerce")

        for int_col in ["src_port", "dst_port", "input_count", "output_count", "transaction_size", "block_height", "asn", "src_asn", "dst_asn"]:
            if int_col in norm_df.columns:
                norm_df[int_col] = pd.to_numeric(norm_df[int_col], errors="coerce").astype("Int64")

        # Standardize timestamps to ISO 8601 UTC
        for ts_col in ["timestamp", "transaction_timestamp"]:
            if ts_col in norm_df.columns:
                parsed_ts = pd.to_datetime(norm_df[ts_col], errors="coerce", utc=True)
                norm_df[ts_col] = parsed_ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return norm_df
