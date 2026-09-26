from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
import pandas as pd
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies & Clusters"])
db = DuckDBManager()

@router.get("")
def get_anomalies(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    only_anomalies: bool = Query(True),
    min_score: float = Query(0.0, ge=0.0, le=1.0)
):
    conn = db.get_connection()
    try:
        where_clauses = []
        params = []

        if only_anomalies:
            where_clauses.append("is_anomaly = TRUE")
        if min_score > 0.0:
            where_clauses.append("anomaly_score >= ?")
            params.append(min_score)

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"SELECT entity_id, anomaly_score, anomaly_score AS normalized_anomaly_score, is_anomaly, cluster_id, pca_x, pca_y, model_type FROM anomalies{where_sql} ORDER BY anomaly_score DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        df = conn.execute(query, params).df()
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    finally:
        conn.close()

@router.get("/clusters")
def get_clusters():
    conn = db.get_connection()
    try:
        df = conn.execute("SELECT cluster_id, COUNT(*) as count, AVG(anomaly_score) as avg_anomaly FROM anomalies GROUP BY cluster_id ORDER BY cluster_id").df()
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    finally:
        conn.close()
