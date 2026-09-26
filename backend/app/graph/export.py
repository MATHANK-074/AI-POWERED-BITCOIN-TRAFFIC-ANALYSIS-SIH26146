import networkx as nx
from typing import Dict, Any, List, Optional

class CytoscapeExporter:
    """
    Exports NetworkX graph data to Cytoscape.js compatible JSON format ({ "nodes": [...], "edges": [...] }).
    Supports filtering by center entity node, max depth, or top degree nodes.
    """
    def export_subgraph(self, G: nx.DiGraph, center_node: Optional[str] = None, max_depth: int = 2, max_nodes: int = 150) -> Dict[str, Any]:
        if G.number_of_nodes() == 0:
            return {"nodes": [], "edges": []}

        if center_node and center_node in G:
            # Subgraph centered on requested node
            sub_nodes = set([center_node])
            current_level = set([center_node])
            for _ in range(max_depth):
                next_level = set()
                for n in current_level:
                    preds = set(G.predecessors(n))
                    succs = set(G.successors(n))
                    next_level.update(preds.union(succs))
                sub_nodes.update(next_level)
                current_level = next_level
                if len(sub_nodes) >= max_nodes:
                    break
            subgraph = G.subgraph(list(sub_nodes)[:max_nodes])
        else:
            # Top degree nodes
            top_nodes = [n for n, d in sorted(G.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]]
            subgraph = G.subgraph(top_nodes)

        nodes = []
        for n, data in subgraph.nodes(data=True):
            node_type = data.get("type", "Wallet")
            nodes.append({
                "data": {
                    "id": n,
                    "label": data.get("label", n[:10]),
                    "type": node_type,
                    "anomaly_score": data.get("anomaly_score", 0.0),
                    "normalized_anomaly_score": data.get("normalized_anomaly_score", 0.0),
                    "is_anomaly": data.get("is_anomaly", False),
                    "cluster_id": data.get("cluster_id", -1),
                    "amount_btc": data.get("amount_btc", 0.0)
                }
            })

        edges = []
        for u, v, data in subgraph.edges(data=True):
            rel = data.get("relationship", data.get("type", "LINKED"))
            edges.append({
                "data": {
                    "id": f"{u}_{v}_{rel}",
                    "source": u,
                    "target": v,
                    "relationship": rel,
                    "amount_btc": data.get("amount_btc", 0.0)
                }
            })

        return {"nodes": nodes, "edges": edges}
