import os
import time
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
    """
    AI/ML Anomaly Detection module using scikit-learn Isolation Forest and StandardScaler.
    Produces raw decision function scores, anomaly labels, and normalized anomaly scores [0.0, 1.0].
    """
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
            return pd.DataFrame(), {
                "total_entities_evaluated": 0,
                "anomalies_detected": 0,
                "contamination_rate": self.contamination,
                "avg_anomaly_score": 0.0,
                "processing_time_sec": 0.0
            }

        available_cols = [c for c in FEATURE_COLS if c in feature_df.columns]
        X = feature_df[available_cols].fillna(0.0).values

        # Scale numerical features with StandardScaler
        X_scaled = self.scaler.fit_transform(X)

        # Fit Isolation Forest
        self.model.fit(X_scaled)

        # Compute raw decision function (lower means more anomalous)
        raw_scores = self.model.decision_function(X_scaled)
        
        # Normalize anomaly scores to [0.0, 1.0] where 1.0 = highly anomalous
        min_s, max_s = raw_scores.min(), raw_scores.max()
        if max_s != min_s:
            norm_scores = 1.0 - (raw_scores - min_s) / (max_s - min_s)
        else:
            norm_scores = np.zeros_like(raw_scores)

        # Predict anomaly labels (-1 = anomaly, 1 = normal)
        preds = self.model.predict(X_scaled)
        is_anomaly = (preds == -1)

        result_df = feature_df.copy()
        result_df["anomaly_score"] = np.round(norm_scores, 4)
        result_df["normalized_anomaly_score"] = np.round(norm_scores, 4)
        result_df["is_anomaly"] = is_anomaly
        result_df["model_type"] = "IsolationForest"

        # Persist trained model and scaler to models/ directory
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.model, os.path.join(MODELS_DIR, "isolation_forest.joblib"))
        joblib.dump(self.scaler, os.path.join(MODELS_DIR, "scaler.joblib"))

        stats = {
            "total_entities_evaluated": len(feature_df),
            "anomalies_detected": int(np.sum(is_anomaly)),
            "contamination_rate": self.contamination,
            "avg_anomaly_score": round(float(np.mean(norm_scores)), 4),
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return result_df, stats
