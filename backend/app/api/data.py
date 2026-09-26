import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import Dict, Any
from app.storage.database import DatabaseManager
from app.config import RAW_DIR
from scripts.run_all import run_pipeline

router = APIRouter(prefix="/api/data", tags=["Data"])
db = DatabaseManager()

@router.get("/statistics")
def get_statistics():
    return db.get_statistics()

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    dest_dir = Path(RAW_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Schedule background pipeline execution
    background_tasks.add_task(run_pipeline, str(dest_path))

    return {
        "filename": file.filename,
        "status": "File uploaded successfully. Processing pipeline started in background.",
        "file_path": str(dest_path)
    }

@router.post("/run-pipeline")
def trigger_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"status": "Full analytics pipeline triggered in background."}
