import shutil
import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Query
from typing import Dict, Any, Optional

from app.ingestion.csv_parser import CSVParser
from app.ingestion.json_parser import JSONParser
from app.ingestion.xml_parser import XMLParser
from app.database.duckdb_manager import DuckDBManager
from app.config import RAW_DIR
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from scripts.run_all import run_pipeline

router = APIRouter(prefix="/api/ingest", tags=["Data Ingestion"])
db = DuckDBManager()

pipeline_status = {
    "is_running": False,
    "last_run_timestamp": None,
    "last_result": None
}

def execute_background_pipeline(file_path: str):
    global pipeline_status
    pipeline_status["is_running"] = True
    try:
        res = run_pipeline(file_path)
        pipeline_status["last_result"] = res
    except Exception as e:
        pipeline_status["last_result"] = {"error": str(e)}
    finally:
        pipeline_status["is_running"] = False
        pipeline_status["last_run_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

@router.post("")
async def ingest_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    dest_dir = Path(RAW_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    suffix = dest_path.suffix.lower()
    if suffix == ".csv":
        parser = CSVParser()
    elif suffix in [".json", ".jsonl"]:
        parser = JSONParser()
    elif suffix == ".xml":
        parser = XMLParser()
    else:
        parser = CSVParser()

    valid_df, rejected_df, stats = parser.parse(str(dest_path))

    # Save to DuckDB
    if not valid_df.empty:
        db.save_transactions(valid_df)
    if not rejected_df.empty:
        db.save_rejected_records(rejected_df)

    # Schedule background analysis
    background_tasks.add_task(execute_background_pipeline, str(dest_path))

    return {
        "status": "File ingested successfully. Analytics pipeline running in background.",
        "ingestion_stats": stats
    }

@router.get("/status")
def get_ingest_status():
    stats = db.get_statistics()
    return {
        "pipeline_running": pipeline_status["is_running"],
        "last_run_timestamp": pipeline_status["last_run_timestamp"],
        "database_stats": stats
    }

@router.get("/map-markers")
def get_map_markers():
    try:
        conn = db.get_connection()
        try:
            # Check if columns exist
            cols = [r[0] for r in conn.execute("DESCRIBE transactions").fetchall()]
            if 'src_lat' in cols and 'src_lon' in cols:
                query = "SELECT src_city, src_lat as lat, src_lon as lon, COUNT(*) as value FROM transactions WHERE src_lat IS NOT NULL AND src_lon IS NOT NULL GROUP BY src_city, src_lat, src_lon HAVING src_lat != 0.0"
                df = conn.execute(query).df()
                markers = []
                for _, row in df.iterrows():
                    markers.append({
                        "name": f"{row['src_city'] or 'Unknown'} ({row['value']})",
                        "coordinates": [row['lon'], row['lat']],
                        "value": row['value']
                    })
                return {"markers": markers}
            return {"markers": []}
        finally:
            conn.close()
    except Exception as e:
        return {"markers": [], "error": str(e)}

