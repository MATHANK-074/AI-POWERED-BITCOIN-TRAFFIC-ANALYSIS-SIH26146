from fastapi import APIRouter
from app.config import CONFIG

router = APIRouter(tags=["System Health"])

@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": CONFIG.get("system", {}).get("name", "KRISHIGUARD"),
        "version": CONFIG.get("system", {}).get("version", "1.0.0"),
        "offline_mode": CONFIG.get("system", {}).get("offline_mode", True)
    }
