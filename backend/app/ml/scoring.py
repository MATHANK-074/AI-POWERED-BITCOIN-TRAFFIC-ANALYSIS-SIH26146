import pandas as pd
from typing import Dict, Any, Tuple
from app.ml.anomaly import AnomalyDetector
from app.ml.clustering import EntityClustering

class MLPipeline:
    """
    Combined ML Pipeline orchestrating Anomaly Detection and Entity Clustering.
    """
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.clustering_engine = EntityClustering(method="kmeans")

    def run_ml_pipeline(self, features_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if features_df.empty:
            return pd.DataFrame(), {"status": "Empty feature dataframe"}

        # 1. Anomaly Detection
        anom_df, anom_stats = self.anomaly_detector.train_and_predict(features_df)

        # 2. Entity Clustering
        clust_df, clust_stats = self.clustering_engine.cluster_and_project(anom_df)

        combined_stats = {
            "anomaly_detection": anom_stats,
            "clustering": clust_stats
        }

        return clust_df, combined_stats
