import time
import networkx as nx
import pandas as pd
from typing import Dict, Any, List, Optional

class KnowledgeGraphEngine:
    def __init__(self):
        self.G = nx.DiGraph()

    def build_graph(self, transactions_df: pd.DataFrame, anomalies_df: pd.DataFrame = None) -> Dict[str, Any]:
        start_time = time.time()
        self.G.clear()

        anomaly_dict = {}
        if anomalies_df is not None and not anomalies_df.empty:
            for _, row in anomalies_df.iterrows():
                anomaly_dict[str(row["entity_id"])] = {
                    "anomaly_score": float(row.get("anomaly_score", 0.0)),
                    "is_anomaly": bool(row.get("is_anomaly", False)),
                    "cluster_id": int(row.get("cluster_id", -1))
                }

        for idx, row in transactions_df.iterrows():
            txid = str(row["txid"])
            src_ip = str(row.get("src_ip", ""))
            in_wallet = str(row.get("input_wallet", ""))
            out_wallet = str(row.get("output_wallet", ""))
            amount = float(row.get("amount_btc", 0.0))
            fee = float(row.get("fee_btc", 0.0))
            ts = str(row.get("transaction_timestamp", ""))

            # Add TXID node
            self.G.add_node(txid, label=txid[:10] + "...", type="txid", amount_btc=amount, fee_btc=fee, timestamp=ts)

            # Add IP node & edge IP -> TXID
            if src_ip:
                ip_anom = anomaly_dict.get(src_ip, {})
                self.G.add_node(src_ip, label=src_ip, type="ip", **ip_anom)
                self.G.add_edge(src_ip, txid, relationship="observed_from_ip")

            # Add Input Wallet node & edge Input Wallet -> TXID
            if in_wallet:
                w_anom = anomaly_dict.get(in_wallet, {})
                self.G.add_node(in_wallet, label=in_wallet[:10] + "...", type="wallet", **w_anom)
                self.G.add_edge(in_wallet, txid, relationship="input_source", amount_btc=amount)

            # Add Output Wallet node & edge TXID -> Output Wallet
            if out_wallet:
                w_anom = anomaly_dict.get(out_wallet, {})
                self.G.add_node(out_wallet, label=out_wallet[:10] + "...", type="wallet", **w_anom)
                self.G.add_edge(txid, out_wallet, relationship="output_destination", amount_btc=amount)

        stats = {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "connected_components": nx.number_weakly_connected_components(self.G) if self.G.number_of_nodes() > 0 else 0,
            "processing_time_sec": round(time.time() - start_time, 4)
        }
        self._compute_advanced_heuristics()

        return stats

    def _compute_advanced_heuristics(self):
        # 1. Personalized PageRank for risk score propagation
        nodes_with_anom = [(n, d.get('anomaly_score', 0.0)) for n, d in self.G.nodes(data=True) if d.get('anomaly_score', 0.0) > 0]
        nodes_with_anom.sort(key=lambda x: x[1], reverse=True)
        # Select top 5% as seeds
        seed_count = max(1, int(len(self.G.nodes()) * 0.05))
        seed_nodes = nodes_with_anom[:seed_count]
        personalization = {n: 0.0 for n in self.G.nodes()}
        if seed_nodes:
            for n, score in seed_nodes:
                personalization[n] = score
            try:
                ppr = nx.pagerank(self.G, personalization=personalization, weight='amount_btc')
            except:
                ppr = nx.pagerank(self.G, personalization=personalization)
            for n, score in ppr.items():
                self.G.nodes[n]['pagerank_risk'] = score
        else:
            for n in self.G.nodes():
                self.G.nodes[n]['pagerank_risk'] = 0.0

        # 2. Peeling Chain & CoinJoin Heuristics
        for n, d in self.G.nodes(data=True):
            if d.get('type') == 'txid':
                in_degree = self.G.in_degree(n)
                out_degree = self.G.out_degree(n)
                
                # CoinJoin heuristic: high number of inputs and outputs
                if in_degree >= 3 and out_degree >= 3:
                    self.G.nodes[n]['is_coinjoin'] = True
                else:
                    self.G.nodes[n]['is_coinjoin'] = False
                
                # Peeling Chain heuristic: 1 input, 2 outputs
                if in_degree == 1 and out_degree == 2:
                    self.G.nodes[n]['is_peeling_chain'] = True
                else:
                    self.G.nodes[n]['is_peeling_chain'] = False

    def get_graph_heuristics_df(self) -> pd.DataFrame:
        data = []
        for n, d in self.G.nodes(data=True):
            data.append({
                "entity_id": n,
                "pagerank_risk": d.get('pagerank_risk', 0.0),
                "is_coinjoin": d.get('is_coinjoin', False),
                "is_peeling_chain": d.get('is_peeling_chain', False)
            })
        return pd.DataFrame(data)

    def get_subgraph_cytoscape(self, center_node: Optional[str] = None, max_depth: int = 2, max_nodes: int = 150) -> Dict[str, Any]:
        """
        Exports Cytoscape.js compatible graph format (nodes & edges lists)
        filtered by depth or top degree nodes.
        """
        if self.G.number_of_nodes() == 0:
            return {"nodes": [], "edges": []}

        if center_node and center_node in self.G:
            # BFS subgraph Ego graph centered on requested entity
            sub_nodes = set([center_node])
            current_level = set([center_node])
            for _ in range(max_depth):
                next_level = set()
                for n in current_level:
                    neighbors = set(self.G.predecessors(n)).union(set(self.G.successors(n)))
                    next_level.update(neighbors)
                sub_nodes.update(next_level)
                current_level = next_level
                if len(sub_nodes) >= max_nodes:
                    break
            subgraph = self.G.subgraph(list(sub_nodes)[:max_nodes])
        else:
            # Return top nodes by degree
            top_nodes = [n for n, d in sorted(self.G.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]]
            subgraph = self.G.subgraph(top_nodes)

        nodes = []
        for n, data in subgraph.nodes(data=True):
            node_type = data.get("type", "wallet")
            nodes.append({
                "data": {
                    "id": n,
                    "label": data.get("label", n[:10]),
                    "type": node_type,
                    "anomaly_score": data.get("anomaly_score", 0.0),
                    "is_anomaly": data.get("is_anomaly", False),
                    "cluster_id": data.get("cluster_id", -1),
                    "amount_btc": data.get("amount_btc", 0.0)
                }
            })

        edges = []
        for u, v, data in subgraph.edges(data=True):
            edges.append({
                "data": {
                    "id": f"{u}_{v}",
                    "source": u,
                    "target": v,
                    "relationship": data.get("relationship", "linked"),
                    "amount_btc": data.get("amount_btc", 0.0)
                }
            })

        return {"nodes": nodes, "edges": edges}
