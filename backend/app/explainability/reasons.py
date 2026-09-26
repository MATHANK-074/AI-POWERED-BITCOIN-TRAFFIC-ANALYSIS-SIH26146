from typing import Dict, Any, List

class ExplainabilityEngine:
    """
    Generates human-readable, feature-driven explanations for flagged entities and transactions.
    """
    def generate_reasons(
        self,
        entity_id: str,
        entity_type: str,
        anomaly_score: float,
        correlation_score: float,
        feature_dict: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> List[str]:
        reasons = []

        # Feature Reason 1: Model Anomaly Score
        if anomaly_score >= 0.8:
            reasons.append(f"Model Anomaly Score ({anomaly_score:.2f}) is in the top critical percentile of learned baseline.")
        elif anomaly_score >= 0.5:
            reasons.append(f"Model Anomaly Score ({anomaly_score:.2f}) deviates significantly from standard behavioral clusters.")

        # Feature Reason 2: Network Correlation
        if correlation_score >= 0.7:
            reasons.append(f"High cross-layer Network-Blockchain temporal correlation ({correlation_score:.2f}) within observed time window.")
        elif correlation_score >= 0.5:
            reasons.append(f"Moderate network activity window match observed with transaction event.")

        # Feature Reason 3: Rule/Pattern indicators
        for pat in patterns:
            reasons.append(f"Detected Pattern [{pat.get('pattern_name')}]: {pat.get('description')}")

        # Feature Reason 4: Transaction Volume / Fan-Out / Rapid Burst
        tx_cnt = feature_dict.get("tx_count", 0)
        tot_amt = feature_dict.get("total_amount_btc", 0.0)
        burst = feature_dict.get("burst_score", 0.0)
        out_deg = feature_dict.get("out_degree", 0)
        in_deg = feature_dict.get("in_degree", 0)

        if tx_cnt >= 20:
            reasons.append(f"Entity exhibits high transaction volume ({tx_cnt} transactions, total volume {tot_amt:.4f} BTC).")

        if burst >= 0.4:
            reasons.append(f"High rapid-fire transaction burst frequency ({burst*100:.1f}% transactions within 10 seconds).")

        if out_deg >= 5 and in_deg <= 2:
            reasons.append(f"High output fan-out topology ({out_deg} destination wallets from single input source).")
        elif in_deg >= 5 and out_deg <= 2:
            reasons.append(f"High fan-in consolidation topology ({in_deg} input sources consolidating funds).")

        if not reasons:
            reasons.append("Entity exhibits baseline transactional patterns with observed network linkages.")

        return reasons
