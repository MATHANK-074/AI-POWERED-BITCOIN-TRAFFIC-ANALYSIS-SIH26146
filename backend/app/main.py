from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api import health, ingestion, transactions, entities, graph, anomalies, leads, evaluation, reports, cases, evidence
from app.config import SERVER_CFG, REPORTS_DIR

app = FastAPI(
    title="KRISHIGUARD - AI-Powered Offline Bitcoin Investigation System",
    description="Offline Forensic Platform for Cryptocurrency Data Ingestion, Network-Blockchain Correlation, AI/ML Anomaly Detection, Entity Clustering, Knowledge Graph Analysis, and Prioritized Lead Generation.",
    version="1.0.0"
)

# Enable CORS for offline React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(ingestion.router)
app.include_router(transactions.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(anomalies.router)
app.include_router(leads.router)
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(evaluation.router)
app.include_router(reports.router)

# Mount static reports directory for viewing
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/reports_static", StaticFiles(directory=REPORTS_DIR), name="reports_static")

# Serve React Frontend
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "system": "KRISHIGUARD",
            "status": "Online (Frontend Build Missing. Run 'npm run build' in frontend/)",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_CFG.get("host", "0.0.0.0"), port=SERVER_CFG.get("port", 8000))
