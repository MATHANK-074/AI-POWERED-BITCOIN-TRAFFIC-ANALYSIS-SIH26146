import sys
import os
import time
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ingestion.csv_parser import CSVParser
from app.ingestion.json_parser import JSONParser
from app.ingestion.xml_parser import XMLParser
from app.validation.validator import DataValidator
from app.storage.database import DatabaseManager
from app.correlation.correlation_engine import CorrelationEngine
from app.features.feature_engineering import FeatureEngine
from app.ml.anomaly_detection import AnomalyDetector
from app.ml.clustering import EntityClustering
from app.graph.graph_analysis import KnowledgeGraphEngine
from app.leads.priority_scoring import PriorityScorer

def run_pipeline(input_file: str = "data/synthetic/synthetic_bitcoin_dataset.csv"):
    start_total = time.time()
    print("=" * 70)
    print(" STARTING OFFLINE BITCOIN INVESTIGATION & ML ANALYTICS PIPELINE")
    print("=" * 70)

    in_path = Path(input_file)
    if not in_path.exists():
        print(f"Error: Input file {input_file} not found. Generating synthetic dataset first...")
        from scripts.generate_dataset import generate_synthetic_dataset
        generate_synthetic_dataset(num_records=100000)

    # STEP 1: Multi-format Ingestion
    print(f"\n[1/7] Ingesting dataset: {input_file}")
    suffix = in_path.suffix.lower()
    if suffix == ".csv":
        parser = CSVParser()
    elif suffix in [".json", ".jsonl"]:
        parser = JSONParser()
    elif suffix == ".xml":
        parser = XMLParser()
    else:
        parser = CSVParser()

    df_valid, df_rejected, meta = parser.parse(str(in_path))
    total_raw = meta.get("total_raw_records", meta.get("records_processed", len(df_valid) + len(df_rejected)))
    print(f" -> Successfully parsed {total_raw:,} raw records in {meta.get('processing_time_sec', 0.0)} seconds.")

    # STEP 2: Validation & Cleaning
    print("\n[2/7] Running Data Validation and Cleaning...")
    print(f" -> Valid records: {meta.get('valid_records', len(df_valid)):,} | Invalid rejected: {meta.get('invalid_records', len(df_rejected)):,}")

    # Save rejected records audit file if any
    if not df_rejected.empty:
        rejected_file = Path("data/processed/rejected_records.csv")
        rejected_file.parent.mkdir(parents=True, exist_ok=True)
        df_rejected.to_csv(rejected_file, index=False)
        print(f" -> Saved rejected records to {rejected_file}")

    # STEP 3: DuckDB Storage
    print("\n[3/7] Storing processed dataset in DuckDB analytical storage...")
    db = DatabaseManager()
    db.save_transactions(df_valid)
    print(" -> DuckDB tables indexed and updated successfully.")

    # STEP 4: Network-Blockchain Correlation Engine
    print("\n[4/7] Running Network-Blockchain Correlation Engine...")
    corr_engine = CorrelationEngine(time_window_sec=10.0)
    df_corr, corr_stats = corr_engine.correlate(df_valid)
    db.save_correlated_events(df_corr)
    print(f" -> Generated {corr_stats['correlated_candidates_found']:,} candidate IP <-> TXID <-> Wallet linkages (Avg Score: {corr_stats['avg_correlation_score']}).")

    # STEP 5: Feature Engineering
    print("\n[5/7] Extracting entity features (Wallets & IPs)...")
    feat_engine = FeatureEngine()
    df_features, feat_stats = feat_engine.extract_features(df_valid)
    db.save_entity_features(df_features)
    print(f" -> Extracted features for {feat_stats['total_entities_extracted']:,} entities ({feat_stats['wallet_entities']:,} wallets, {feat_stats['ip_entities']:,} IPs).")

    # STEP 6: AI/ML Anomaly Detection & Clustering
    print("\n[6/7] Running Isolation Forest Anomaly Detection & DBSCAN Clustering...")
    anom_detector = AnomalyDetector(contamination=0.05)
    df_anom, anom_stats = anom_detector.train_and_predict(df_features)
    
    # Build a preliminary graph for Node2Vec
    graph_engine = KnowledgeGraphEngine()
    graph_engine.build_graph(df_valid, df_anom)
    
    clustering = EntityClustering(method="dbscan", eps=0.5, min_samples=5)
    df_anom, cluster_stats = clustering.cluster_and_project(df_anom, graph_engine=graph_engine, transactions_df=df_valid)
    db.save_anomalies(df_anom)
    print(f" -> Detected {anom_stats['anomalies_detected']:,} anomalous entities across {cluster_stats['unique_clusters_found']} clusters (Silhouette Score: {cluster_stats['silhouette_score']}).")

    # STEP 7: Graph Analysis & Investigation Leads
    print("\n[7/7] Building Knowledge Graph & Scoring Priority Leads...")
    
    # Update graph nodes with latest cluster info if necessary
    g_stats = graph_engine.build_graph(df_valid, df_anom)
    graph_heuristics_df = graph_engine.get_graph_heuristics_df()
    
    # Merge graph heuristics into features for priority scoring
    df_features_enriched = df_features.merge(graph_heuristics_df, on="entity_id", how="left")
    
    scorer = PriorityScorer()
    df_leads, lead_stats = scorer.generate_leads(df_features_enriched, df_anom, df_corr, df_valid)
    db.save_investigation_leads(df_leads)
    
    print(f" -> Built Knowledge Graph ({g_stats['total_nodes']:,} nodes, {g_stats['total_edges']:,} edges).")
    print(f" -> Generated {lead_stats['total_leads_generated']:,} prioritized investigation leads ({lead_stats.get('critical_priority_count', 0)} Critical, {lead_stats.get('high_priority_count', 0)} High, {lead_stats.get('medium_priority_count', 0)} Medium).")

    elapsed = round(time.time() - start_total, 2)
    print("=" * 70)
    print(f" PIPELINE EXECUTION COMPLETE IN {elapsed} SECONDS")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
