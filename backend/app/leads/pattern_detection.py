import pandas as pd
from typing import Dict, Any, List

class PatternDetector:
    def detect_patterns_for_entity(self, entity_id: str, feature_row: Dict[str, Any], entity_txs: pd.DataFrame) -> List[Dict[str, Any]]:
        patterns = []

        tx_count = feature_row.get("tx_count", 0)
        burst_score = feature_row.get("burst_score", 0.0)
        in_degree = feature_row.get("in_degree", 0)
        out_degree = feature_row.get("out_degree", 0)
        avg_fee = feature_row.get("avg_fee_btc", 0.0)
        avg_amt = feature_row.get("avg_amount_btc", 0.0)
        unique_ips = feature_row.get("unique_ip_count", 0)
        unique_counterparties = feature_row.get("unique_counterparties", 0)

        # 1. Burst Activity
        if burst_score > 0.4:
            patterns.append({
                "pattern_id": "PAT_BURST",
                "pattern_name": "Burst Activity",
                "description": f"High density of rapid-fire transactions ({burst_score*100:.1f}% occurring within 10 seconds of prior transaction).",
                "severity": "high" if burst_score > 0.7 else "medium"
            })

        # 2. Fan-In Aggregation
        if in_degree >= 5 and out_degree <= 2:
            patterns.append({
                "pattern_id": "PAT_FAN_IN",
                "pattern_name": "Fan-In Consolidation",
                "description": f"Multiple incoming transaction sources ({in_degree} input wallets) consolidating into a single recipient.",
                "severity": "medium"
            })

        # 3. Fan-Out Distribution
        if out_degree >= 5 and in_degree <= 2:
            patterns.append({
                "pattern_id": "PAT_FAN_OUT",
                "pattern_name": "Fan-Out Distribution",
                "description": f"Single source wallet fanning out funds to multiple distinct output recipients ({out_degree} destination wallets).",
                "severity": "medium"
            })

        # 4. High-Frequency Activity
        if tx_count >= 20:
            patterns.append({
                "pattern_id": "PAT_HIGH_FREQ",
                "pattern_name": "High-Frequency Entity",
                "description": f"Abnormally high transaction frequency ({tx_count} transactions) relative to dataset baseline.",
                "severity": "high" if tx_count >= 50 else "medium"
            })

        # 5. Unusual Fee Behavior
        if avg_amt > 0 and (avg_fee / max(0.0001, avg_amt)) > 0.05:
            patterns.append({
                "pattern_id": "PAT_UNUSUAL_FEE",
                "pattern_name": "Unusual Miner Fee",
                "description": f"Unusually high transaction fee ratio ({avg_fee:.6f} BTC fee per transaction relative to amount {avg_amt:.4f} BTC).",
                "severity": "high"
            })

        # 6. Network Concentration
        if unique_ips >= 5 or (entity_row_type := feature_row.get("entity_type")) == "ip" and unique_counterparties >= 10:
            patterns.append({
                "pattern_id": "PAT_NET_CONC",
                "pattern_name": "Network Concentration",
                "description": f"Entity observed across multiple network IP locations ({unique_ips} distinct IPs) or handling high counterparty fanout.",
                "severity": "medium"
            })

        return patterns
