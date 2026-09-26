import networkx as nx
from typing import Dict, Any, List, Optional

class GraphAnalyzer:
    """
    Graph analysis engine for querying neighbors, paths, connected components,
    degree centrality, and suspicious entity clusters in NetworkX graph.
    """
    def __init__(self, G: nx.DiGraph):
        self.G = G

    def find_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        if node_id not in self.G:
            return []

        neighbors = []
        for successor in self.G.successors(node_id):
            edge_data = self.G.get_edge_data(node_id, successor) or {}
            node_data = self.G.nodes[successor]
            neighbors.append({
                "direction": "outgoing",
                "target_id": successor,
                "node_type": node_data.get("type", "Unknown"),
                "relationship": edge_data.get("relationship", "LINKED")
            })

        for predecessor in self.G.predecessors(node_id):
            edge_data = self.G.get_edge_data(predecessor, node_id) or {}
            node_data = self.G.nodes[predecessor]
            neighbors.append({
                "direction": "incoming",
                "source_id": predecessor,
                "node_type": node_data.get("type", "Unknown"),
                "relationship": edge_data.get("relationship", "LINKED")
            })

        return neighbors

    def find_shortest_path(self, source_id: str, target_id: str) -> List[str]:
        if source_id not in self.G or target_id not in self.G:
            return []
        try:
            return nx.shortest_path(self.G.to_undirected(), source=source_id, target=target_id)
        except nx.NetworkXNoPath:
            return []

    def get_high_degree_nodes(self, top_n: int = 20) -> List[Dict[str, Any]]:
        if self.G.number_of_nodes() == 0:
            return []

        degree_dict = dict(self.G.degree())
        sorted_nodes = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]

        result = []
        for n, deg in sorted_nodes:
            data = self.G.nodes[n]
            result.append({
                "entity_id": n,
                "degree": deg,
                "in_degree": self.G.in_degree(n),
                "out_degree": self.G.out_degree(n),
                "node_type": data.get("type", "Unknown"),
                "anomaly_score": data.get("anomaly_score", 0.0),
                "is_anomaly": data.get("is_anomaly", False)
            })

        return result

    def get_suspicious_clusters(self, min_anomaly_score: float = 0.7) -> List[Dict[str, Any]]:
        if self.G.number_of_nodes() == 0:
            return []

        suspicious_nodes = [
            n for n, data in self.G.nodes(data=True)
            if data.get("is_anomaly") or data.get("anomaly_score", 0.0) >= min_anomaly_score
        ]

        if not suspicious_nodes:
            return []

        subgraph = self.G.subgraph(suspicious_nodes).to_undirected()
        components = list(nx.connected_components(subgraph))

        clusters = []
        for idx, comp in enumerate(components):
            comp_nodes = list(comp)
            avg_score = sum(self.G.nodes[n].get("anomaly_score", 0.0) for n in comp_nodes) / len(comp_nodes)
            clusters.append({
                "cluster_id": idx + 1,
                "node_count": len(comp_nodes),
                "nodes": comp_nodes[:20],
                "avg_anomaly_score": round(avg_score, 4)
            })

        return sorted(clusters, key=lambda x: x["node_count"], reverse=True)
