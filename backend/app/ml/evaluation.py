import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, silhouette_score

class ModelEvaluator:
    """
    Evaluates ML models for both supervised datasets (with ground-truth labels)
    and unsupervised datasets (without manufacturing fake metrics).
    """
    def evaluate(self, df: pd.DataFrame, label_col: str = "synthetic_pattern_label") -> Dict[str, Any]:
        if df.empty:
            return {"status": "No data available for evaluation"}

        has_ground_truth = label_col in df.columns and df[label_col].notna().sum() > 0

        if has_ground_truth:
            # Binary ground truth: map positive labels vs normal (0)
            y_true = df[label_col].apply(lambda x: 0 if str(x).lower() in ["normal_activity", "normal", "none", "nan", "0", "false", ""] else 1).values
            y_pred = df["is_anomaly"].astype(int).values if "is_anomaly" in df.columns else np.zeros(len(df))
            y_scores = df["anomaly_score"].values if "anomaly_score" in df.columns else np.zeros(len(df))

            precision = float(precision_score(y_true, y_pred, zero_division=0))
            recall = float(recall_score(y_true, y_pred, zero_division=0))
            f1 = float(f1_score(y_true, y_pred, zero_division=0))

            try:
                auc = float(roc_auc_score(y_true, y_scores)) if len(np.unique(y_true)) > 1 else 0.0
            except Exception:
                auc = 0.0

            cm = confusion_matrix(y_true, y_pred).tolist() if len(np.unique(y_true)) > 1 else []

            return {
                "evaluation_type": "Supervised Ground Truth Evaluation",
                "ground_truth_column": label_col,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(auc, 4),
                "confusion_matrix": cm,
                "total_samples": len(df),
                "positive_ground_truth_count": int(np.sum(y_true == 1))
            }
        else:
            # Unsupervised metrics
            total = len(df)
            anom_count = int(df["is_anomaly"].sum()) if "is_anomaly" in df.columns else 0
            anom_ratio = round(anom_count / max(1, total), 4)

            avg_score = float(df["anomaly_score"].mean()) if "anomaly_score" in df.columns else 0.0

            cluster_dist = df["cluster_id"].value_counts().to_dict() if "cluster_id" in df.columns else {}

            return {
                "evaluation_type": "Unsupervised Metrics (No Ground Truth Labels Present)",
                "total_entities_evaluated": total,
                "anomalies_detected": anom_count,
                "anomaly_rate": anom_ratio,
                "avg_anomaly_score": round(avg_score, 4),
                "cluster_size_distribution": {str(k): int(v) for k, v in cluster_dist.items()}
            }
