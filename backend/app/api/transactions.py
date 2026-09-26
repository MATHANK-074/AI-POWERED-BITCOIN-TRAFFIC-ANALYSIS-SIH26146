from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import pandas as pd
from app.database.duckdb_manager import DuckDBManager

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])
db = DuckDBManager()

@router.get("")
def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    txid: Optional[str] = None,
    wallet: Optional[str] = None,
    ip: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
):
    conn = db.get_connection()
    try:
        where_clauses = []
        params = []

        if txid:
            where_clauses.append("txid LIKE ?")
            params.append(f"%{txid}%")
        if wallet:
            where_clauses.append("(input_wallet LIKE ? OR output_wallet LIKE ?)")
            params.extend([f"%{wallet}%", f"%{wallet}%"])
        if ip:
            where_clauses.append("(src_ip LIKE ? OR dst_ip LIKE ?)")
            params.extend([f"%{ip}%", f"%{ip}%"])
        if min_amount is not None:
            where_clauses.append("amount_btc >= ?")
            params.append(min_amount)
        if max_amount is not None:
            where_clauses.append("amount_btc <= ?")
            params.append(max_amount)

        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        query = f"SELECT * FROM transactions{where_sql} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        df = conn.execute(query, params).df()
        
        # Replace NaN with None for JSON serialization
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    finally:
        conn.close()

@router.get("/{txid}")
def get_transaction_by_txid(txid: str):
    conn = db.get_connection()
    try:
        res = conn.execute("SELECT * FROM transactions WHERE txid = ?", [txid]).df()
        if res.empty:
            raise HTTPException(status_code=44, detail=f"Transaction {txid} not found")
        res = res.where(pd.notnull(res), None)
        return res.to_dict(orient="records")[0]
    finally:
        conn.close()
