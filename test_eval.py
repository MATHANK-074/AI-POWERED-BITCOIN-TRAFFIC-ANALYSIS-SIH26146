import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
from app.ml.evaluation import ModelEvaluator
from app.database.duckdb_manager import DuckDBManager

db = DuckDBManager()
conn = db.get_connection()
df = conn.execute("SELECT t.*, a.anomaly_score, a.is_anomaly FROM transactions t LEFT JOIN anomalies a ON t.synthetic_entity_id = a.entity_id").df()
conn.close()
print(f"Entities: {len(df)}")
evaluator = ModelEvaluator()
metrics = evaluator.evaluate(df)
print(metrics)
