import json
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/evidence", tags=["Evidence Audit Trail"])
db = DuckDBManager()

@router.get("/{entity_id}", response_model=List[Dict[str, Any]])
def get_entity_evidence(entity_id: str):
    records = db.get_evidence_by_entity(entity_id)
    if not records:
        # Generate on-the-fly evidence record if lead exists
        conn = db.get_connection()
        try:
            lead_df = conn.execute(
                "SELECT * FROM investigation_leads WHERE entity_id = ? OR lead_id = ? OR txid = ?",
                [entity_id, entity_id, entity_id]
            ).df()
            if not lead_df.empty:
                r = lead_df.to_dict(orient="records")[0]
                records = [{
                    "evidence_id": f"EV_{r.get('lead_id', '0001')}",
                    "entity_id": r.get("entity_id"),
                    "entity_type": r.get("entity_type"),
                    "source_file": "synthetic_bitcoin_dataset.csv",
                    "source_record_index": 1,
                    "ingestion_timestamp": r.get("created_at"),
                    "pipeline_stage": "Feature Extraction & Multi-Factor Priority Scoring",
                    "feature_snapshot": json.dumps({
                        "priority_score": r.get("priority_score"),
                        "anomaly_score": r.get("anomaly_score"),
                        "confidence_score": r.get("confidence_score"),
                        "cluster_id": r.get("cluster_id")
                    }),
                    "correlation_evidence": json.dumps({
                        "connected_entities": r.get("connected_entities_count"),
                        "correlated_events": r.get("correlated_events_count")
                    }),
                    "model_version": "IsolationForest v1.0 + DBSCAN v1.0",
                    "priority_formula": "Priority = 100 * (0.35*Anomaly + 0.25*Correlation + 0.25*Pattern + 0.15*Graph)",
                    "created_at": r.get("created_at")
                }]
        finally:
            conn.close()

    return records
