from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, Optional
from app.storage.database import DatabaseManager

router = APIRouter(prefix="/api/ips", tags=["IPs"])
db = DatabaseManager()

@router.get("")
def get_ips(
    query: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500)
):
    conn = db.get_connection()
    try:
        where_sql = " WHERE entity_type = 'ip'"
        params = []

        if query:
            where_sql += " AND entity_id LIKE ?"
            params.append(f"%{query.strip()}%")

        total_count = conn.execute(f"SELECT COUNT(*) FROM entity_features{where_sql}", params).fetchone()[0]

        offset = (page - 1) * limit
        params_paged = params + [limit, offset]

        sql = f"""
            SELECT ef.*, a.anomaly_score, a.is_anomaly, a.cluster_id
            FROM entity_features ef
            LEFT JOIN anomalies a ON ef.entity_id = a.entity_id
            {where_sql}
            ORDER BY ef.tx_count DESC
            LIMIT ? OFFSET ?
        """
        df = conn.execute(sql, params_paged).df()
        records = df.to_dict(orient="records") if not df.empty else []

        return {
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit,
            "data": records
        }
    finally:
        conn.close()

@router.get("/{ip_address:path}")
def get_ip_detail(ip_address: str):
    conn = db.get_connection()
    try:
        feat_res = conn.execute("SELECT * FROM entity_features WHERE entity_id = ?", [ip_address]).df()
        if feat_res.empty:
            raise HTTPException(status_code=404, detail=f"IP address {ip_address} not found")

        ip_data = feat_res.iloc[0].to_dict()

        # Join Anomaly data if present
        anom_res = conn.execute("SELECT * FROM anomalies WHERE entity_id = ?", [ip_address]).df()
        if not anom_res.empty:
            ip_data.update(anom_res.iloc[0].to_dict())

        # Observed transactions from this IP
        tx_res = conn.execute(
            "SELECT * FROM transactions WHERE src_ip = ? ORDER BY transaction_timestamp DESC LIMIT 100",
            [ip_address]
        ).df()
        ip_data["observed_transactions"] = tx_res.to_dict(orient="records") if not tx_res.empty else []

        # Correlated candidate events
        corr_res = conn.execute("SELECT * FROM correlated_events WHERE src_ip = ? LIMIT 100", [ip_address]).df()
        ip_data["correlated_events"] = corr_res.to_dict(orient="records") if not corr_res.empty else []

        return ip_data
    finally:
        conn.close()
