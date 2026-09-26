import time
import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.config import ML_CFG, MODELS_DIR

FEATURE_COLS = [
    "tx_count", "total_amount_btc", "avg_amount_btc", "max_amount_btc",
    "avg_fee_btc", "unique_ip_count", "unique_counterparties",
    "in_degree", "out_degree", "in_out_ratio", "burst_score", "avg_inter_tx_time_sec"
]

class AnomalyDetector:
    def __init__(self, contamination: float = None, n_estimators: int = None, random_state: int = None):
        self.contamination = contamination or ML_CFG.get("anomaly_contamination", 0.05)
        self.n_estimators = n_estimators or ML_CFG.get("anomaly_n_estimators", 100)
        self.random_state = random_state or ML_CFG.get("random_state", 42)
        
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )

    def train_and_predict(self, feature_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()
        
        if feature_df.empty:
            return pd.DataFrame(), {"anomaly_count": 0}

        # Filter available feature columns
        available_cols = [c for c in FEATURE_COLS if c in feature_df.columns]
        X = feature_df[available_cols].fillna(0).values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit Isolation Forest
        self.model.fit(X_scaled)

        # Raw decision function (lower means more anomalous)
        raw_scores = self.model.decision_function(X_scaled)
        # Normalize anomaly scores to [0.0, 1.0] range where 1.0 = highly anomalous
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s != min_s:
            norm_scores = 1.0 - (raw_scores - min_s) / (max_s - min_s)
        else:
            norm_scores = np.zeros_like(raw_scores)

        preds = self.model.predict(X_scaled) # -1 for anomaly, 1 for normal
        is_anomaly = (preds == -1)

        result_df = feature_df.copy()
        result_df["anomaly_score"] = np.round(norm_scores, 4)
        result_df["is_anomaly"] = is_anomaly
        result_df["model_type"] = "IsolationForest"

        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.model, os.path.join(MODELS_DIR, "isolation_forest.joblib"))
        joblib.dump(self.scaler, os.path.join(MODELS_DIR, "scaler.joblib"))

        stats = {
            "total_entities_evaluated": len(feature_df),
            "anomalies_detected": int(np.sum(is_anomaly)),
            "contamination_rate": self.contamination,
            "avg_anomaly_score": float(np.mean(norm_scores)),
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return result_df, stats
