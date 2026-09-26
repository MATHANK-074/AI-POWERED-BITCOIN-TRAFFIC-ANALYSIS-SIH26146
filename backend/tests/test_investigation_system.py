import pytest
import os
import pandas as pd
from pathlib import Path

from app.ingestion.csv_parser import CSVParser
from app.ingestion.json_parser import JSONParser
from app.ingestion.xml_parser import XMLParser
from app.validation.validator import DataValidator
from app.correlation.correlation_engine import CorrelationEngine
from app.features.feature_engineering import FeatureEngine
from app.ml.anomaly_detection import AnomalyDetector
from app.ml.clustering import EntityClustering
from app.graph.graph_analysis import KnowledgeGraphEngine
from app.leads.priority_scoring import PriorityScorer

TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"

def test_csv_parser():
    csv_file = TEST_DATA_DIR / "synthetic_bitcoin_dataset.csv"
    if csv_file.exists():
        parser = CSVParser()
        df, rejected_df, meta = parser.parse(str(csv_file))
        assert meta.get("total_raw_records", meta.get("records_processed", 0)) > 0
        assert "txid" in df.columns
        assert "input_wallet" in df.columns

def test_data_validator():
    validator = DataValidator()
    # Test valid dataframe
    df_valid = pd.DataFrame([{
        "timestamp": "2026-01-01T12:00:00Z",
        "src_ip": "192.168.1.100",
        "src_port": 8333,
        "dst_ip": "10.0.0.1",
        "dst_port": 8333,
        "txid": "abc123txid",
        "input_wallet": "bc1qtest1",
        "output_wallet": "bc1qtest2",
        "amount_btc": 1.5,
        "fee_btc": 0.0001
    }])
    val_df, rej_df, stats = validator.validate_and_clean(df_valid)
    assert stats["records_valid"] == 1
    assert stats["records_invalid"] == 0

    # Test invalid IP and negative amount
    df_invalid = pd.DataFrame([{
        "timestamp": "2026-01-01T12:00:00Z",
        "src_ip": "999.999.999.999", # Bad IP
        "src_port": 8333,
        "dst_ip": "10.0.0.1",
        "dst_port": 8333,
        "txid": "abc123txid",
        "input_wallet": "bc1qtest1",
        "output_wallet": "bc1qtest2",
        "amount_btc": -5.0, # Negative amount
        "fee_btc": 0.0001
    }])
    val_df_bad, rej_df_bad, stats_bad = validator.validate_and_clean(df_invalid)
    assert stats_bad["records_valid"] == 0
    assert stats_bad["records_invalid"] == 1

def test_correlation_engine():
    engine = CorrelationEngine(time_window_sec=10.0)
    df = pd.DataFrame([{
        "timestamp": "2026-01-01T12:00:00Z",
        "transaction_timestamp": "2026-01-01T12:00:02Z", # 2 seconds delta
        "txid": "tx001",
        "src_ip": "192.168.1.1",
        "input_wallet": "w1",
        "output_wallet": "w2"
    }])
    corr_df, stats = engine.correlate(df)
    assert stats["correlated_candidates_found"] == 1
    assert corr_df.iloc[0]["time_delta_sec"] == 2.0
    assert corr_df.iloc[0]["correlation_score"] > 0.8

def test_feature_engineering_and_ml():
    df = pd.DataFrame([
        {
            "timestamp": "2026-01-01T12:00:00Z",
            "transaction_timestamp": "2026-01-01T12:00:00Z",
            "txid": f"tx_{i}",
            "input_wallet": "w_sender",
            "output_wallet": f"w_receiver_{i%5}",
            "amount_btc": 0.5 + i*0.1,
            "fee_btc": 0.001,
            "src_ip": "192.168.1.50",
            "src_port": 8333,
            "dst_ip": "10.0.0.1",
            "dst_port": 8333
        } for i in range(25)
    ])

    feat_engine = FeatureEngine()
    feat_df, feat_stats = feat_engine.extract_features(df)
    assert feat_stats["total_entities_extracted"] > 0

    anom_detector = AnomalyDetector(contamination=0.1)
    anom_df, anom_stats = anom_detector.train_and_predict(feat_df)
    assert "anomaly_score" in anom_df.columns

    clustering = EntityClustering(method="dbscan")
    cluster_df, cluster_stats = clustering.cluster_and_project(anom_df)
    assert "cluster_id" in cluster_df.columns
    assert "pca_x" in cluster_df.columns

def test_knowledge_graph():
    df = pd.DataFrame([{
        "txid": "tx100",
        "src_ip": "192.168.1.10",
        "input_wallet": "w_in",
        "output_wallet": "w_out",
        "amount_btc": 2.0,
        "fee_btc": 0.001,
        "transaction_timestamp": "2026-01-01T12:00:00Z"
    }])
    graph_engine = KnowledgeGraphEngine()
    stats = graph_engine.build_graph(df)
    assert stats["total_nodes"] == 4 # 1 IP + 1 TXID + 1 Input Wallet + 1 Output Wallet
    sub = graph_engine.get_subgraph_cytoscape()
    assert len(sub["nodes"]) > 0
