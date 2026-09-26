import os
import yaml
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

CONFIG = load_config()

# Convenient exports
STORAGE_CFG = CONFIG.get("storage", {})
CORRELATION_CFG = CONFIG.get("correlation", {})
ML_CFG = CONFIG.get("ml", {})
PRIORITY_CFG = CONFIG.get("priority_scoring", {})
VALIDATION_CFG = CONFIG.get("validation", {})
SERVER_CFG = CONFIG.get("server", {})

DUCKDB_PATH = str(BASE_DIR / STORAGE_CFG.get("duckdb_path", "data/processed/bitcoin_investigation.duckdb"))
REJECTED_RECORDS_PATH = str(BASE_DIR / STORAGE_CFG.get("rejected_records_path", "data/processed/rejected_records.csv"))
RAW_DIR = str(BASE_DIR / STORAGE_CFG.get("raw_dir", "data/raw"))
SYNTHETIC_DIR = str(BASE_DIR / STORAGE_CFG.get("synthetic_dir", "data/synthetic"))
REPORTS_DIR = str(BASE_DIR / STORAGE_CFG.get("reports_dir", "reports"))
MODELS_DIR = str(BASE_DIR / "models")
