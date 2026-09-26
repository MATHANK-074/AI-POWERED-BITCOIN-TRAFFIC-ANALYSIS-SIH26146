import os
import time
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import networkx as nx
from app.config import ML_CFG, MODELS_DIR

FEATURE_COLS = [
    "tx_count", "total_amount_btc", "avg_amount_btc", "max_amount_btc",
    "avg_fee_btc", "unique_ip_count", "unique_counterparties",
    "in_degree", "out_degree", "in_out_ratio", "burst_score",
    "cio_cluster_size", "n2v_x", "n2v_y"
]

class EntityClustering:
    """
    AI/ML Entity Behavior Clustering using K-Means (or DBSCAN) and StandardScaler.
    Outputs cluster IDs, cluster sizes, centroid distances, and PCA 2D coordinates for UI visualization.
    """
    def __init__(self, method: str = "kmeans", n_clusters: int = None, eps: float = None, min_samples: int = None):
        self.method = method.lower()
        self.n_clusters = n_clusters or ML_CFG.get("kmeans_clusters", 5)
        self.eps = eps or ML_CFG.get("dbscan_eps", 0.5)
        self.min_samples = min_samples or ML_CFG.get("dbscan_min_samples", 5)

    def _compute_cio(self, feature_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        if transactions_df is None or transactions_df.empty:
            feature_df["cio_cluster_size"] = 1.0
            return feature_df
        
        # Common-Input-Ownership (CIO) heuristic
        input_groups = transactions_df.groupby("txid")["input_wallet"].apply(list)
        
        # Connected components of wallets
        G_cio = nx.Graph()
        for wallets in input_groups:
            wallets = [w for w in wallets if w and str(w) != 'nan']
            if len(wallets) > 1:
                for i in range(len(wallets) - 1):
                    G_cio.add_edge(wallets[i], wallets[i+1])
            elif len(wallets) == 1:
                G_cio.add_node(wallets[0])
                
        cio_sizes = {}
        for comp in nx.connected_components(G_cio):
            size = len(comp)
            for w in comp:
                cio_sizes[w] = size
                
        feature_df["cio_cluster_size"] = feature_df["entity_id"].map(lambda x: cio_sizes.get(x, 1.0))
        return feature_df

    def _compute_node2vec(self, feature_df: pd.DataFrame, graph_engine) -> pd.DataFrame:
        feature_df["n2v_x"] = 0.0
        feature_df["n2v_y"] = 0.0
        if graph_engine is None or len(graph_engine.G.nodes()) == 0:
            return feature_df
            
        try:
            from node2vec import Node2Vec
            n2v = Node2Vec(graph_engine.G, dimensions=2, walk_length=10, num_walks=10, workers=1, p=1, q=1, quiet=True)
            model = n2v.fit(window=5, min_count=1)
            def get_emb(node, idx):
                if str(node) in model.wv:
                    return model.wv[str(node)][idx]
                return 0.0
            feature_df["n2v_x"] = feature_df["entity_id"].map(lambda x: get_emb(x, 0))
            feature_df["n2v_y"] = feature_df["entity_id"].map(lambda x: get_emb(x, 1))
        except ImportError:
            # Fallback to SVD on Adjacency Matrix if node2vec is not available
            nodelist = list(graph_engine.G.nodes())
            A = nx.to_scipy_sparse_array(graph_engine.G, nodelist=nodelist)
            svd = TruncatedSVD(n_components=2, random_state=42)
            try:
                emb = svd.fit_transform(A)
                emb_dict = {node: emb[i] for i, node in enumerate(nodelist)}
                feature_df["n2v_x"] = feature_df["entity_id"].map(lambda x: emb_dict.get(x, [0.0, 0.0])[0])
                feature_df["n2v_y"] = feature_df["entity_id"].map(lambda x: emb_dict.get(x, [0.0, 0.0])[1])
            except Exception:
                pass
                
        return feature_df

    def cluster_and_project(self, feature_df: pd.DataFrame, graph_engine=None, transactions_df=None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()

        if feature_df.empty:
            return pd.DataFrame(), {
                "clustering_algorithm": self.method,
                "unique_clusters_found": 0,
                "silhouette_score": 0.0,
                "processing_time_sec": 0.0
            }

        # Compute new heuristics
        feature_df = self._compute_cio(feature_df, transactions_df)
        feature_df = self._compute_node2vec(feature_df, graph_engine)

        available_cols = [c for c in FEATURE_COLS if c in feature_df.columns]
        X = feature_df[available_cols].fillna(0.0).values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        if self.method == "kmeans":
            # Adjust n_clusters if dataset is smaller than n_clusters
            k = min(self.n_clusters, len(feature_df))
            k = max(1, k)
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = model.fit_predict(X_scaled)
            
            # Compute distance to assigned centroid
            centroids = model.cluster_centers_
            distances = np.linalg.norm(X_scaled - centroids[cluster_labels], axis=1)
        else:
            model = DBSCAN(eps=self.eps, min_samples=self.min_samples)
            cluster_labels = model.fit_predict(X_scaled)
            distances = np.zeros(len(feature_df))

        # 2D PCA projection for visualization
        n_comp = min(2, X_scaled.shape[1])
        pca = PCA(n_components=n_comp, random_state=42)
        X_pca = pca.fit_transform(X_scaled)

        result_df = feature_df.copy()
        result_df["cluster_id"] = cluster_labels
        result_df["centroid_distance"] = np.round(distances, 4)
        result_df["pca_x"] = np.round(X_pca[:, 0], 4) if n_comp >= 1 else 0.0
        result_df["pca_y"] = np.round(X_pca[:, 1], 4) if n_comp >= 2 else 0.0

        # Compute silhouette score if valid
        unique_labels = set(cluster_labels)
        if len(unique_labels) > 1 and len(unique_labels) < len(feature_df):
            try:
                sil_score = float(silhouette_score(X_scaled, cluster_labels))
            except Exception:
                sil_score = 0.0
        else:
            sil_score = 0.0

        # Cluster size distribution
        cluster_sizes = {int(c): int(np.sum(cluster_labels == c)) for c in unique_labels}

        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(model, os.path.join(MODELS_DIR, f"{self.method}_clustering.joblib"))

        stats = {
            "clustering_algorithm": self.method,
            "unique_clusters_found": len(unique_labels),
            "cluster_sizes": cluster_sizes,
            "silhouette_score": round(sil_score, 4),
            "pca_explained_variance": [round(float(v), 4) for v in pca.explained_variance_ratio_],
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return result_df, stats
