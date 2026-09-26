import duckdb
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import DUCKDB_PATH, REJECTED_RECORDS_PATH

class DuckDBManager:
    """
    High-performance analytical DuckDB database manager for KRISHIGUARD.
    Manages transactions, network correlation, entity features, anomalies, clusters, and leads.
    """
    def __init__(self, db_path: str = DUCKDB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_schema(self):
        conn = self.get_connection()
        try:
            # 1. Transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    txid VARCHAR PRIMARY KEY,
                    timestamp VARCHAR,
                    src_ip VARCHAR,
                    src_port INTEGER,
                    dst_ip VARCHAR,
                    dst_port INTEGER,
                    protocol VARCHAR,
                    network_event_id VARCHAR,
                    input_wallet VARCHAR,
                    output_wallet VARCHAR,
                    amount_btc DOUBLE,
                    fee_btc DOUBLE,
                    script_type VARCHAR,
                    block_height INTEGER,
                    transaction_timestamp VARCHAR,
                    input_count INTEGER,
                    output_count INTEGER,
                    transaction_size INTEGER,
                    asn INTEGER,
                    country VARCHAR,
                    city VARCHAR,
                    src_lat DOUBLE,
                    src_lon DOUBLE,
                    dst_lat DOUBLE,
                    dst_lon DOUBLE,
                    synthetic_entity_id VARCHAR,
                    synthetic_behavior_type VARCHAR,
                    synthetic_pattern_label VARCHAR
                );
            """)

            # 2. Rejected Records / Ingestion Audit Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rejected_records (
                    rejection_id VARCHAR,
                    source_file VARCHAR,
                    rejection_reason VARCHAR,
                    rejected_at VARCHAR,
                    raw_data VARCHAR
                );
            """)

            # 3. Correlated Events Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS correlated_events (
                    correlation_id VARCHAR PRIMARY KEY,
                    txid VARCHAR,
                    src_ip VARCHAR,
                    dst_ip VARCHAR,
                    input_wallet VARCHAR,
                    output_wallet VARCHAR,
                    net_timestamp VARCHAR,
                    tx_timestamp VARCHAR,
                    time_delta_sec DOUBLE,
                    temporal_score DOUBLE,
                    network_match_score DOUBLE,
                    correlation_score DOUBLE,
                    confidence_level VARCHAR
                );
            """)

            # 4. Entity Features Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entity_features (
                    entity_id VARCHAR PRIMARY KEY,
                    entity_type VARCHAR, -- 'wallet', 'ip', 'txid'
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

            # 5. Anomalies & Clusters Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    entity_id VARCHAR PRIMARY KEY,
                    anomaly_score DOUBLE,
                    normalized_anomaly_score DOUBLE,
                    is_anomaly BOOLEAN,
                    cluster_id INTEGER,
                    centroid_distance DOUBLE,
                    pca_x DOUBLE,
                    pca_y DOUBLE,
                    model_type VARCHAR,
                    updated_at VARCHAR
                );
            """)

            # 6. Investigation Leads Table
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
                    reasons VARCHAR, -- JSON string array
                    supporting_evidence TEXT,
                    created_at VARCHAR
                );
            """)

            # 7. Investigation Cases Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS investigation_cases (
                    case_id VARCHAR PRIMARY KEY,
                    title VARCHAR,
                    description TEXT,
                    status VARCHAR, -- 'OPEN', 'UNDER INVESTIGATION', 'RESOLVED', 'ARCHIVED'
                    assigned_to VARCHAR,
                    entities VARCHAR, -- JSON string array of entity IDs/wallets
                    leads VARCHAR, -- JSON string array of lead IDs
                    notes TEXT,
                    created_at VARCHAR,
                    updated_at VARCHAR
                );
            """)

            # 8. Evidence Audit Trail Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_audit_trail (
                    evidence_id VARCHAR PRIMARY KEY,
                    entity_id VARCHAR,
                    entity_type VARCHAR,
                    source_file VARCHAR,
                    source_record_index INTEGER,
                    ingestion_timestamp VARCHAR,
                    pipeline_stage VARCHAR,
                    feature_snapshot TEXT, -- JSON string of extracted features
                    correlation_evidence TEXT, -- JSON string of correlation matches
                    model_version VARCHAR,
                    priority_formula VARCHAR,
                    created_at VARCHAR
                );
            """)
        finally:
            conn.close()

    def save_transactions(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            # Match columns dynamically with transactions table
            db_cols = [r[0] for r in conn.execute("DESCRIBE transactions").fetchall()]
            df_cols = [c for c in db_cols if c in df.columns]
            sub_df = df[df_cols]
            col_names = ", ".join(df_cols)
            conn.execute(f"INSERT OR REPLACE INTO transactions ({col_names}) SELECT * FROM sub_df")
        finally:
            conn.close()

    def save_rejected_records(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            conn.execute("INSERT INTO rejected_records SELECT * FROM df")
        finally:
            conn.close()

    def save_correlated_events(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO correlated_events SELECT * FROM df")
        finally:
            conn.close()

    def save_entity_features(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO entity_features SELECT * FROM df")
        finally:
            conn.close()

    def save_anomalies(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            db_cols = [r[0] for r in conn.execute("DESCRIBE anomalies").fetchall()]
            cols = [c for c in db_cols if c in df.columns]
            sub_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO anomalies SELECT * FROM sub_df")
        finally:
            conn.close()

    def save_investigation_leads(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            db_cols = [r[0] for r in conn.execute("DESCRIBE investigation_leads").fetchall()]
            cols = [c for c in db_cols if c in df.columns]
            sub_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO investigation_leads SELECT * FROM sub_df")
        finally:
            conn.close()

    def get_transactions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            rel = conn.execute(f"SELECT * FROM transactions LIMIT {limit} OFFSET {offset}").df()
            return rel.to_dict(orient="records")
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        conn = self.get_connection()
        try:
            total_txs = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            total_wallets = conn.execute("""
                SELECT COUNT(DISTINCT w) FROM (
                    SELECT input_wallet AS w FROM transactions WHERE input_wallet IS NOT NULL AND input_wallet != ''
                    UNION
                    SELECT output_wallet AS w FROM transactions WHERE output_wallet IS NOT NULL AND output_wallet != ''
                )
            """).fetchone()[0]
            total_ips = conn.execute("SELECT COUNT(DISTINCT src_ip) FROM transactions WHERE src_ip IS NOT NULL AND src_ip != ''").fetchone()[0]
            correlated_count = conn.execute("SELECT COUNT(*) FROM correlated_events").fetchone()[0]
            anomalies_count = conn.execute("SELECT COUNT(*) FROM anomalies WHERE is_anomaly = TRUE").fetchone()[0]
            leads_count = conn.execute("SELECT COUNT(*) FROM investigation_leads").fetchone()[0]

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
        try:
            res = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?", [table_name]).fetchone()
            return res[0] > 0 if res else False
        except Exception:
            return False

    def save_case(self, case_dict: Dict[str, Any]):
        conn = self.get_connection()
        try:
            df = pd.DataFrame([case_dict])
            db_cols = [r[0] for r in conn.execute("DESCRIBE investigation_cases").fetchall()]
            cols = [c for c in db_cols if c in df.columns]
            sub_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO investigation_cases SELECT * FROM sub_df")
        finally:
            conn.close()

    def get_cases(self) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            if not self._table_exists(conn, "investigation_cases"):
                return []
            df = conn.execute("SELECT * FROM investigation_cases ORDER BY updated_at DESC").df()
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        finally:
            conn.close()

    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            if not self._table_exists(conn, "investigation_cases"):
                return None
            df = conn.execute("SELECT * FROM investigation_cases WHERE case_id = ?", [case_id]).df()
            if df.empty:
                return None
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")[0]
        finally:
            conn.close()

    def delete_case(self, case_id: str) -> bool:
        conn = self.get_connection()
        try:
            if not self._table_exists(conn, "investigation_cases"):
                return False
            conn.execute("DELETE FROM investigation_cases WHERE case_id = ?", [case_id])
            return True
        finally:
            conn.close()

    def save_evidence_records(self, df: pd.DataFrame):
        if df.empty:
            return
        conn = self.get_connection()
        try:
            db_cols = [r[0] for r in conn.execute("DESCRIBE evidence_audit_trail").fetchall()]
            cols = [c for c in db_cols if c in df.columns]
            sub_df = df[cols]
            conn.execute("INSERT OR REPLACE INTO evidence_audit_trail SELECT * FROM sub_df")
        finally:
            conn.close()

    def get_evidence_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            if not self._table_exists(conn, "evidence_audit_trail"):
                return []
            df = conn.execute("SELECT * FROM evidence_audit_trail WHERE entity_id = ? ORDER BY created_at DESC", [entity_id]).df()
            if df.empty:
                df = conn.execute("SELECT * FROM evidence_audit_trail WHERE evidence_id LIKE ? LIMIT 10", [f"%{entity_id}%"]).df()
            df = df.where(pd.notnull(df), None)
            return df.to_dict(orient="records")
        finally:
            conn.close()
