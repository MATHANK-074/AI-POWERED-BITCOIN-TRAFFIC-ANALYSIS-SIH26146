from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
import pandas as pd
from app.database.duckdb_manager import DuckDBManager
from app.graph.builder import KnowledgeGraphBuilder
from app.graph.export import CytoscapeExporter
from app.graph.analysis import GraphAnalyzer

router = APIRouter(prefix="/api/graph", tags=["Investigation Graph"])
db = DuckDBManager()
builder = KnowledgeGraphBuilder()
exporter = CytoscapeExporter()

@router.get("")
@router.get("/{node_id}")
def get_investigation_graph(
    node_id: Optional[str] = None,
    max_depth: int = Query(2, ge=1, le=5),
    max_nodes: int = Query(150, ge=10, le=500)
):
    conn = db.get_connection()
    try:
        txs = conn.execute("SELECT * FROM transactions LIMIT 1000").df() if db._table_exists(conn, "transactions") else pd.DataFrame()
        anom = conn.execute("SELECT * FROM anomalies").df() if db._table_exists(conn, "anomalies") else pd.DataFrame()
        
        builder.build_graph(txs, anom)
        cyto_data = exporter.export_subgraph(builder.G, center_node=node_id, max_depth=max_depth, max_nodes=max_nodes)
        
        analyzer = GraphAnalyzer(builder.G)
        top_degree = analyzer.get_high_degree_nodes(top_n=10)

        return {
            "graph": cyto_data,
            "center_node": node_id,
            "statistics": {
                "total_graph_nodes": builder.G.number_of_nodes(),
                "total_graph_edges": builder.G.number_of_edges(),
                "rendered_nodes": len(cyto_data["nodes"]),
                "rendered_edges": len(cyto_data["edges"])
            },
            "top_high_degree_entities": top_degree
        }
    finally:
        conn.close()

@router.get("/path/search")
def search_shortest_path(source: str, target: str):
    conn = db.get_connection()
    try:
        txs = conn.execute("SELECT * FROM transactions LIMIT 2000").df() if db._table_exists(conn, "transactions") else pd.DataFrame()
        anom = conn.execute("SELECT * FROM anomalies").df() if db._table_exists(conn, "anomalies") else pd.DataFrame()
        builder.build_graph(txs, anom)
        analyzer = GraphAnalyzer(builder.G)
        
        path_nodes = analyzer.find_shortest_path(source, target)
        if not path_nodes:
            return {"source": source, "target": target, "path_found": False, "path_nodes": [], "graph": {"nodes": [], "edges": []}}
        
        subgraph_cyto = exporter.export_subgraph(builder.G, center_node=source, max_depth=len(path_nodes)+1, max_nodes=200)
        return {
            "source": source,
            "target": target,
            "path_found": True,
            "path_length": len(path_nodes) - 1,
            "path_nodes": path_nodes,
            "graph": subgraph_cyto
        }
    finally:
        conn.close()

@router.get("/neighbors/{node_id}")
def get_node_neighbors(node_id: str):
    conn = db.get_connection()
    try:
        txs = conn.execute("SELECT * FROM transactions LIMIT 1000").df() if db._table_exists(conn, "transactions") else pd.DataFrame()
        builder.build_graph(txs)
        analyzer = GraphAnalyzer(builder.G)
        neighbors = analyzer.find_neighbors(node_id)
        return {"node_id": node_id, "total_neighbors": len(neighbors), "neighbors": neighbors}
    finally:
        conn.close()
