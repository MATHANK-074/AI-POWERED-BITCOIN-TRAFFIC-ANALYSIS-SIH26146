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
            entity_labels = {}
            for _, r in txs.iterrows():
                lbl = str(r.get("synthetic_pattern_label", "normal_activity"))
                if lbl and lbl.lower() not in ["normal_activity", "normal", "none", "nan"]:
                    for col in ["input_wallet", "output_wallet", "src_ip", "synthetic_entity_id"]:
                        val = str(r.get(col, ""))
                        if val and val != "nan":
                            entity_labels[val] = lbl
            
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
