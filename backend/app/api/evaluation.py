from fastapi import APIRouter
from typing import Dict, Any
import pandas as pd
from app.database.duckdb_manager import DuckDBManager
from app.ml.evaluation import ModelEvaluator

router = APIRouter(prefix="/api/evaluation", tags=["Model Evaluation"])
db = DuckDBManager()
evaluator = ModelEvaluator()

@router.get("")
def get_model_evaluation():
    conn = db.get_connection()
    try:
        anom = conn.execute("SELECT * FROM anomalies").df() if db._table_exists(conn, "anomalies") else pd.DataFrame()
        txs = conn.execute("SELECT * FROM transactions").df() if db._table_exists(conn, "transactions") else pd.DataFrame()
        
        if not anom.empty and not txs.empty:
            entity_anom_counts = {}
            entity_total_counts = {}
            entity_labels = {}
            
            for _, r in txs.iterrows():
                lbl = str(r.get("synthetic_pattern_label", "normal_activity")).lower()
                is_anom = lbl not in ["normal_activity", "normal", "none", "nan", "0", "false", ""]
                
                for col in ["input_wallet", "output_wallet", "src_ip", "synthetic_entity_id"]:
                    val = str(r.get(col, ""))
                    if val and val != "nan":
                        entity_total_counts[val] = entity_total_counts.get(val, 0) + 1
                        if is_anom:
                            entity_anom_counts[val] = entity_anom_counts.get(val, 0) + 1
                            # Store the label to use if they pass the threshold
                            entity_labels[val] = str(r.get("synthetic_pattern_label"))

            # Only label entity as anomaly if > 25% of their transactions are anomalous
            for val, anom_count in entity_anom_counts.items():
                total = entity_total_counts.get(val, 1)
                if (anom_count / total) < 0.25:
                    entity_labels.pop(val, None)
            
            anom_copy = anom.copy()
            anom_copy["synthetic_pattern_label"] = anom_copy["entity_id"].map(lambda x: entity_labels.get(str(x), "normal_activity"))
            res = evaluator.evaluate(anom_copy, label_col="synthetic_pattern_label")
        elif not anom.empty:
            res = evaluator.evaluate(anom, label_col="synthetic_pattern_label")
        else:
            res = {"status": "No trained model or anomaly evaluation records found."}

        return res
    finally:
        conn.close()
