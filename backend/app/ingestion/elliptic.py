import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import pandas as pd
from app.ingestion.validator import DataValidator

class EllipticDatasetParser:
    """
    Parser for the Elliptic Bitcoin dataset:
    - elliptic_txs_classes.csv (txId, class: 1=illicit, 2=licit, unknown)
    - elliptic_txs_edgelist.csv (txId1, txId2)
    - elliptic_txs_features.csv (txId, time_step, feature_0 ... feature_165)
    """
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else None
        self.validator = DataValidator()

    def parse_elliptic_dataset(
        self,
        classes_path: str,
        edgelist_path: str,
        features_path: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        
        c_path = Path(classes_path)
        e_path = Path(edgelist_path)
        f_path = Path(features_path)

        if not c_path.exists() or not e_path.exists() or not f_path.exists():
            raise FileNotFoundError("One or more Elliptic dataset files were not found.")

        # Read classes
        df_classes = pd.read_csv(c_path)
        # Rename columns if needed
        df_classes.columns = [c.strip() for c in df_classes.columns]
        if "txId" in df_classes.columns:
            df_classes.rename(columns={"txId": "txid", "class": "synthetic_pattern_label"}, inplace=True)

        # Map class labels (1 = illicit, 2 = licit, unknown = unknown)
        df_classes["synthetic_pattern_label"] = df_classes["synthetic_pattern_label"].astype(str).map({
            "1": "illicit",
            "2": "licit",
            "unknown": "unknown"
        }).fillna("unknown")

        # Read edgelist
        df_edges = pd.read_csv(e_path)
        df_edges.columns = [c.strip() for c in df_edges.columns]
        if "txId1" in df_edges.columns:
            df_edges.rename(columns={"txId1": "txid", "txId2": "output_wallet"}, inplace=True)

        # Read features
        df_features = pd.read_csv(f_path, header=None)
        # First column is txId, second is time step
        tx_col = df_features.columns[0]
        step_col = df_features.columns[1]
        
        df_features.rename(columns={tx_col: "txid", step_col: "time_step"}, inplace=True)

        # Merge classes with features
        df_merged = pd.merge(df_classes, df_features[["txid", "time_step"]], on="txid", how="inner")
        
        # Add standardized fields expected by system
        df_merged["timestamp"] = df_merged["time_step"].apply(lambda s: f"2026-01-01T{int(s)%24:02d}:00:00Z")
        df_merged["transaction_timestamp"] = df_merged["timestamp"]
        df_merged["amount_btc"] = 1.0
        df_merged["fee_btc"] = 0.0001
        df_merged["src_ip"] = "Network evidence unavailable"
        df_merged["input_wallet"] = df_merged["txid"].apply(lambda t: f"w_in_{t}")
        df_merged["output_wallet"] = df_merged["txid"].apply(lambda t: f"w_out_{t}")

        valid_df, rejected_df, stats = self.validator.validate(
            df=df_merged,
            source_file=c_path.name,
            source_format="Elliptic Dataset"
        )

        stats["processing_time_sec"] = round(time.time() - start_time, 4)
        stats["elliptic_edges_count"] = len(df_edges)
        stats["elliptic_illicit_count"] = int((df_classes["synthetic_pattern_label"] == "illicit").sum())

        return valid_df, df_edges, stats
