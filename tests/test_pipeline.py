import os
import pytest
import pandas as pd
from app.ingestion.normalizer import SchemaNormalizer
from app.ingestion.validator import DataValidator
from app.correlation.network_blockchain import NetworkBlockchainCorrelator
from app.features.feature_engineering import FeatureEngine
from app.ml.anomaly import AnomalyDetector
from app.ml.clustering import EntityClustering
from app.graph.builder import KnowledgeGraphBuilder
from app.graph.export import CytoscapeExporter
from app.explainability.lead_generator import LeadGenerator

def test_schema_normalizer(sample_transactions_df):
    normalizer = SchemaNormalizer()
    mapped_df, _ = normalizer.map_columns(sample_transactions_df)
    norm_df = normalizer.normalize_fields(mapped_df)
    assert "txid" in norm_df.columns
    assert len(norm_df) == 2

def test_data_validator(sample_transactions_df):
    validator = DataValidator()
    valid_df, rejected_df, stats = validator.validate(sample_transactions_df)
    assert stats["valid_records"] == 2
    assert stats["invalid_records"] == 0

def test_correlator(sample_transactions_df):
    correlator = NetworkBlockchainCorrelator(time_window_sec=10.0)
    corr_df, stats = correlator.correlate(sample_transactions_df)
    assert len(corr_df) == 2
    assert "correlation_score" in corr_df.columns

def test_feature_engineering(sample_transactions_df):
    engine = FeatureEngine()
    feat_df, stats = engine.extract_features(sample_transactions_df)
    assert not feat_df.empty
    assert "tx_count" in feat_df.columns

def test_anomaly_and_clustering(sample_transactions_df):
    engine = FeatureEngine()
    feat_df, _ = engine.extract_features(sample_transactions_df)
    
    anom_detector = AnomalyDetector()
    anom_df, anom_stats = anom_detector.train_and_predict(feat_df)
    assert "anomaly_score" in anom_df.columns

    clustering = EntityClustering(method="kmeans", n_clusters=2)
    clust_df, clust_stats = clustering.cluster_and_project(anom_df)
    assert "cluster_id" in clust_df.columns

def test_graph_builder(sample_transactions_df):
    builder = KnowledgeGraphBuilder()
    stats = builder.build_graph(sample_transactions_df)
    assert stats["total_nodes"] > 0
    assert stats["total_edges"] > 0

    exporter = CytoscapeExporter()
    cyto_data = exporter.export_subgraph(builder.G)
    assert "nodes" in cyto_data
    assert "edges" in cyto_data

def test_lead_generation(sample_transactions_df):
    engine = FeatureEngine()
    feat_df, _ = engine.extract_features(sample_transactions_df)

    anom_detector = AnomalyDetector()
    anom_df, _ = anom_detector.train_and_predict(feat_df)

    correlator = NetworkBlockchainCorrelator()
    corr_df, _ = correlator.correlate(sample_transactions_df)

    lead_gen = LeadGenerator()
    leads_df, lead_stats = lead_gen.generate_leads(feat_df, anom_df, corr_df, sample_transactions_df)
    assert not leads_df.empty
    assert "priority_score" in leads_df.columns

def test_case_management():
    from app.database.duckdb_manager import DuckDBManager
    db = DuckDBManager()
    test_case = {
        "case_id": "CASE_TEST_001",
        "title": "Test Case Investigation",
        "description": "Unit test case",
        "status": "OPEN",
        "assigned_to": "Test Investigator",
        "entities": '["192.168.1.100", "bc1qtest1"]',
        "leads": '["LEAD_000001"]',
        "notes": "Test case notes",
        "created_at": "2026-01-01T12:00:00Z",
        "updated_at": "2026-01-01T12:00:00Z"
    }
    db.save_case(test_case)
    retrieved = db.get_case_by_id("CASE_TEST_001")
    assert retrieved is not None
    assert retrieved["title"] == "Test Case Investigation"
    
    cases_list = db.get_cases()
    assert len(cases_list) > 0

    deleted = db.delete_case("CASE_TEST_001")
    assert deleted is True

def test_evidence_audit_trail():
    from app.database.duckdb_manager import DuckDBManager
    db = DuckDBManager()
    ev_df = pd.DataFrame([{
        "evidence_id": "EV_TEST_001",
        "entity_id": "192.168.1.100",
        "entity_type": "ip",
        "source_file": "test_data.csv",
        "source_record_index": 42,
        "ingestion_timestamp": "2026-01-01T12:00:00Z",
        "pipeline_stage": "Feature Extraction",
        "feature_snapshot": '{"priority_score": 85.0}',
        "correlation_evidence": '{"connected_entities": 5}',
        "model_version": "IsolationForest v1.0",
        "priority_formula": "Standard Priority Formula",
        "created_at": "2026-01-01T12:00:00Z"
    }])
    db.save_evidence_records(ev_df)
    ev_list = db.get_evidence_by_entity("192.168.1.100")
    assert len(ev_list) > 0
    assert ev_list[0]["source_file"] == "test_data.csv"

def test_graph_path_search(sample_transactions_df):
    from app.graph.analysis import GraphAnalyzer
    builder = KnowledgeGraphBuilder()
    builder.build_graph(sample_transactions_df)
    analyzer = GraphAnalyzer(builder.G)
    
    nodes = list(builder.G.nodes())
    if len(nodes) >= 2:
        path = analyzer.find_shortest_path(nodes[0], nodes[1])
        # Path is a list of node IDs if path exists, or empty list
        assert isinstance(path, list)

def test_data_enrichment(sample_transactions_df):
    from app.ingestion.enrichment import OfflineEnricher
    enricher = OfflineEnricher()
    enriched_df = enricher.enrich_dataframe(sample_transactions_df, is_synthetic=True)
    assert "data_provenance" in enriched_df.columns
    assert enriched_df["data_provenance"].iloc[0] == "SYNTHETIC/DEMO DATA"

