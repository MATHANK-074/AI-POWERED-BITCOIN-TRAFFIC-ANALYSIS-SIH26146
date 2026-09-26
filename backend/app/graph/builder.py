import time
import networkx as nx
import pandas as pd
from typing import Dict, Any, Optional

class KnowledgeGraphBuilder:
    """
    Builds a heterogenous NetworkX Directed Multi-Graph (DiGraph) for Bitcoin transactions and network observations.
    Node Types: IP, Wallet, Transaction, Entity, ASN, Geo
    Edge Types: SENT, RECEIVED, OBSERVED_FROM, CONNECTED_TO, RELATED_TO, SAME_CLUSTER, CORRELATED_WITH
    """
    def __init__(self):
        self.G = nx.DiGraph()

    def build_graph(self, transactions_df: pd.DataFrame, anomalies_df: pd.DataFrame = None) -> Dict[str, Any]:
        start_time = time.time()
        self.G.clear()

        if transactions_df.empty:
            return {"total_nodes": 0, "total_edges": 0, "connected_components": 0, "processing_time_sec": 0.0}

        # Map anomaly & cluster attributes if present
        anom_map = {}
        if anomalies_df is not None and not anomalies_df.empty:
            for _, row in anomalies_df.iterrows():
                anom_map[str(row["entity_id"])] = {
                    "anomaly_score": float(row.get("anomaly_score", 0.0)),
                    "normalized_anomaly_score": float(row.get("normalized_anomaly_score", row.get("anomaly_score", 0.0))),
                    "is_anomaly": bool(row.get("is_anomaly", False)),
                    "cluster_id": int(row.get("cluster_id", -1))
                }

        for idx, row in transactions_df.iterrows():
            txid = str(row.get("txid", ""))
            src_ip = str(row.get("src_ip", ""))
            dst_ip = str(row.get("dst_ip", ""))
            in_wallet = str(row.get("input_wallet", ""))
            out_wallet = str(row.get("output_wallet", ""))
            amount = float(row.get("amount_btc", 0.0))
            fee = float(row.get("fee_btc", 0.0))
            ts = str(row.get("timestamp", row.get("transaction_timestamp", "")))
            asn = str(row.get("asn", "UNKNOWN")) if pd.notna(row.get("asn")) else "UNKNOWN"
            country = str(row.get("country", "UNKNOWN")) if pd.notna(row.get("country")) else "UNKNOWN"

            if not txid or txid == "nan":
                continue

            tx_anom = anom_map.get(txid, {})
            # Add Transaction Node
            self.G.add_node(
                txid,
                label=txid[:10] + "...",
                type="Transaction",
                amount_btc=amount,
                fee_btc=fee,
                timestamp=ts,
                **tx_anom
            )

            # Add Source IP Node & Edge: OBSERVED_FROM
            if src_ip and src_ip != "UNKNOWN" and src_ip != "nan":
                ip_anom = anom_map.get(src_ip, {})
                self.G.add_node(src_ip, label=src_ip, type="IP", **ip_anom)
                self.G.add_edge(src_ip, txid, relationship="OBSERVED_FROM", type="OBSERVED_FROM")

            # Add Destination IP Node if present
            if dst_ip and dst_ip != "UNKNOWN" and dst_ip != "nan":
                self.G.add_node(dst_ip, label=dst_ip, type="IP")
                self.G.add_edge(txid, dst_ip, relationship="CONNECTED_TO", type="CONNECTED_TO")

            # Add ASN Node & Edge if available
            if asn != "UNKNOWN" and asn != "nan":
                asn_node = f"ASN_{asn}"
                self.G.add_node(asn_node, label=f"ASN {asn}", type="ASN")
                if src_ip and src_ip != "UNKNOWN":
                    self.G.add_edge(src_ip, asn_node, relationship="RELATED_TO", type="RELATED_TO")

            # Add Country Geo Node & Edge if available
            if country != "UNKNOWN" and country != "nan":
                geo_node = f"GEO_{country}"
                self.G.add_node(geo_node, label=f"Geo: {country}", type="Geo")
                if src_ip and src_ip != "UNKNOWN":
                    self.G.add_edge(src_ip, geo_node, relationship="LOCATED_IN", type="LOCATED_IN")

            # Add Input Wallet & Edge: SENT
            if in_wallet and in_wallet != "UNKNOWN" and in_wallet != "nan":
                w_anom = anom_map.get(in_wallet, {})
                self.G.add_node(in_wallet, label=in_wallet[:10] + "...", type="Wallet", **w_anom)
                self.G.add_edge(in_wallet, txid, relationship="SENT", type="SENT", amount_btc=amount)

            # Add Output Wallet & Edge: RECEIVED
            if out_wallet and out_wallet != "UNKNOWN" and out_wallet != "nan":
                w_anom = anom_map.get(out_wallet, {})
                self.G.add_node(out_wallet, label=out_wallet[:10] + "...", type="Wallet", **w_anom)
                self.G.add_edge(txid, out_wallet, relationship="RECEIVED", type="RECEIVED", amount_btc=amount)

        stats = {
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "connected_components": nx.number_weakly_connected_components(self.G) if self.G.number_of_nodes() > 0 else 0,
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return stats
