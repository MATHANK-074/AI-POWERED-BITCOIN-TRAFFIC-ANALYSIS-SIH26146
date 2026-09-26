import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/cases", tags=["Case Management"])
db = DuckDBManager()

class CaseCreateSchema(BaseModel):
    title: str = Field(..., description="Case Title")
    description: Optional[str] = Field("", description="Detailed Case Description")
    status: str = Field("OPEN", description="OPEN, UNDER INVESTIGATION, RESOLVED, ARCHIVED")
    assigned_to: Optional[str] = Field("Investigator Admin", description="Assigned Investigator Name")
    entities: List[str] = Field(default_factory=list, description="Target Wallet/IP Entity IDs")
    leads: List[str] = Field(default_factory=list, description="Linked Lead IDs")
    notes: Optional[str] = Field("", description="Investigator Analysis Notes")

class CaseUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    entities: Optional[List[str]] = None
    leads: Optional[List[str]] = None
    notes: Optional[str] = None

@router.get("", response_model=List[Dict[str, Any]])
def get_all_cases():
    return db.get_cases()

@router.post("", response_model=Dict[str, Any])
def create_case(payload: CaseCreateSchema):
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cases = db.get_cases()
    case_id = f"CASE_{len(cases) + 1:04d}"
    
    case_dict = {
        "case_id": case_id,
        "title": payload.title,
        "description": payload.description or "",
        "status": payload.status.upper(),
        "assigned_to": payload.assigned_to or "Unassigned",
        "entities": json.dumps(payload.entities),
        "leads": json.dumps(payload.leads),
        "notes": payload.notes or "",
        "created_at": now_utc,
        "updated_at": now_utc
    }
    db.save_case(case_dict)
    return case_dict

@router.get("/{case_id}")
def get_case(case_id: str):
    c = db.get_case_by_id(case_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return c

@router.put("/{case_id}")
def update_case(case_id: str, payload: CaseUpdateSchema):
    existing = db.get_case_by_id(case_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if payload.title is not None:
        existing["title"] = payload.title
    if payload.description is not None:
        existing["description"] = payload.description
    if payload.status is not None:
        existing["status"] = payload.status.upper()
    if payload.assigned_to is not None:
        existing["assigned_to"] = payload.assigned_to
    if payload.entities is not None:
        existing["entities"] = json.dumps(payload.entities)
    if payload.leads is not None:
        existing["leads"] = json.dumps(payload.leads)
    if payload.notes is not None:
        existing["notes"] = payload.notes

    existing["updated_at"] = now_utc
    db.save_case(existing)
    return existing

@router.delete("/{case_id}")
def delete_case(case_id: str):
    success = db.delete_case(case_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return {"status": "success", "message": f"Case {case_id} deleted successfully"}

@router.get("/{case_id}/export")
def export_case_report(case_id: str):
    c = db.get_case_by_id(case_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    # Fetch linked leads and evidence details
    linked_leads = []
    try:
        lead_ids = json.loads(c.get("leads", "[]"))
        conn = db.get_connection()
        try:
            for lid in lead_ids:
                df = conn.execute("SELECT * FROM investigation_leads WHERE lead_id = ?", [lid]).df()
                if not df.empty:
                    linked_leads.append(df.to_dict(orient="records")[0])
        finally:
            conn.close()
    except Exception:
        pass

    report = {
        "case_report_id": f"REPORT_{c['case_id']}",
        "export_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "case_details": c,
        "total_linked_leads": len(linked_leads),
        "linked_leads": linked_leads,
        "disclaimer": "OFFLINE INVESTIGATION DECISION SUPPORT REPORT. MODEL INDICATORS DO NOT CONSTITUTE PROOF OF ILLEGALITY."
    }
    return report
