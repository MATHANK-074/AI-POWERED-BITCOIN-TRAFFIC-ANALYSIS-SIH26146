import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import DUCKDB_PATH, REJECTED_RECORDS_PATH

class DatabaseManager:
    def __init__(self, db_path: str = DUCKDB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_tables(self):
        conn = self.get_connection()
        try:
            # 1. Transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    timestamp VARCHAR,
                    src_ip VARCHAR,
                    src_port INTEGER,
                    dst_ip VARCHAR,
                    dst_port INTEGER,
                    src_country VARCHAR,
                    src_city VARCHAR,
                    src_lat DOUBLE,
                    src_lon DOUBLE,
                    src_asn INTEGER,
                    dst_country VARCHAR,
                    dst_city VARCHAR,
                    dst_lat DOUBLE,
                    dst_lon DOUBLE,
                    dst_asn INTEGER,
                    network_event_id VARCHAR,
                    protocol VARCHAR,
                    txid VARCHAR PRIMARY KEY,
                    input_wallet VARCHAR,
                    output_wallet VARCHAR,
                    amount_btc DOUBLE,
                    fee_btc DOUBLE,
                    script_type VARCHAR,
                    block_height INTEGER,
                    transaction_timestamp VARCHAR,
                    synthetic_entity_id VARCHAR,
                    synthetic_behavior_type VARCHAR,
                    synthetic_pattern_label VARCHAR
                );
            """)

            # 2. Correlated Events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS correlated_events (
                    correlation_id VARCHAR PRIMARY KEY,
                    txid VARCHAR,
                    src_ip VARCHAR,
                    input_wallet VARCHAR,
                    output_wallet VARCHAR,
                    net_timestamp VARCHAR,
                    tx_timestamp VARCHAR,
                    time_delta_sec DOUBLE,
                    temporal_score DOUBLE,
                    network_match_score DOUBLE,
                    correlation_score DOUBLE
                );
            """)

            # 3. Entity Features table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entity_features (
                    entity_id VARCHAR PRIMARY KEY,
                    entity_type VARCHAR, -- 'wallet' or 'ip'
                    tx_count INTEGER,
                    total_amount_btc DOUBLE,
                    avg_amount_btc DOUBLE,
                    max_amount_btc DOUBLE,
                    min_amount_btc DOUBLE,
                    avg_fee_btc DOUBLE,
                    unique_ip_count INTEGER,
                    unique_port_count INTEGER,
                    unique_counterparties INTEGER,
                    in_degree INTEGER,
                    out_degree INTEGER,
                    in_out_ratio DOUBLE,
                    burst_score DOUBLE,
                    avg_inter_tx_time_sec DOUBLE
                );
            """)

            # 4. Anomalies table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    entity_id VARCHAR PRIMARY KEY,
                    anomaly_score DOUBLE,
                    is_anomaly BOOLEAN,
                    cluster_id INTEGER,
                    pca_x DOUBLE,
                    pca_y DOUBLE,
                    model_type VARCHAR
                );
            """)

            # 5. Investigation Leads table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS investigation_leads (
                    lead_id VARCHAR PRIMARY KEY,
                    entity_id VARCHAR,
                    txid VARCHAR,
                    entity_type VARCHAR,
                    priority_score DOUBLE,
                    priority_level VARCHAR, -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
                    anomaly_score DOUBLE,
                    confidence_score DOUBLE,
                    cluster_id INTEGER,
                    connected_entities_count INTEGER,
                    correlated_events_count INTEGER,
                    reasons VARCHAR,
                    supporting_evidence TEXT,
                    created_at VARCHAR
                );
            """)
        finally:
            conn.close()

    def save_transactions(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO transactions BY NAME SELECT * FROM df")
        finally:
            conn.close()

    def save_correlated_events(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO correlated_events SELECT * FROM df")
        finally:
            conn.close()

    def save_entity_features(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO entity_features SELECT * FROM df")
        finally:
            conn.close()

    def save_anomalies(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            cols = ["entity_id", "anomaly_score", "is_anomaly", "cluster_id", "pca_x", "pca_y", "model_type"]
            subset_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO anomalies SELECT * FROM subset_df")
        finally:
            conn.close()

    def save_investigation_leads(self, df: pd.DataFrame):
        conn = self.get_connection()
        try:
            cols = [
                "lead_id", "entity_id", "txid", "entity_type", "priority_score",
                "priority_level", "anomaly_score", "confidence_score", "cluster_id",
                "connected_entities_count", "correlated_events_count", "reasons",
                "supporting_evidence", "created_at"
            ]
            subset_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO investigation_leads SELECT * FROM subset_df")
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            total_txs = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            total_wallets = conn.execute("SELECT COUNT(DISTINCT wallet) FROM (SELECT input_wallet as wallet FROM transactions UNION SELECT output_wallet as wallet FROM transactions)").fetchone()[0]
            total_ips = conn.execute("SELECT COUNT(DISTINCT src_ip) FROM transactions").fetchone()[0]
            correlated_count = conn.execute("SELECT COUNT(*) FROM correlated_events").fetchone()[0]
            anomalies_count = conn.execute("SELECT COUNT(*) FROM anomalies WHERE is_anomaly = TRUE").fetchone()[0] if self._table_exists(conn, "anomalies") else 0
            leads_count = conn.execute("SELECT COUNT(*) FROM investigation_leads").fetchone()[0] if self._table_exists(conn, "investigation_leads") else 0
            
            return {
                "total_transactions": total_txs,
                "total_wallets": total_wallets,
                "total_ips": total_ips,
                "correlated_events": correlated_count,
                "anomalies_detected": anomalies_count,
                "investigation_leads": leads_count
            }
        finally:
            conn.close()

    def _table_exists(self, conn, table_name: str) -> bool:
        res = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [table_name]).fetchone()
        return res[0] > 0
