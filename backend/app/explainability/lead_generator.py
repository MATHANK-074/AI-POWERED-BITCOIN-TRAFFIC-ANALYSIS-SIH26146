import json
import time
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from app.explainability.reasons import ExplainabilityEngine
from app.leads.pattern_detection import PatternDetector
from app.config import PRIORITY_CFG

class LeadGenerator:
    """
    Generates ranked, prioritized investigative leads combining:
    - Anomaly Score
    - Cluster Risk
    - Graph Topology Risk
    - Network Correlation Confidence
    - Behavioral Pattern Indicators

    Priority Levels: CRITICAL (>=85), HIGH (>=70), MEDIUM (>=40), LOW (<40).
    """
    def __init__(self):
        self.explainability_engine = ExplainabilityEngine()
        self.pattern_detector = PatternDetector()
        weights = PRIORITY_CFG.get("weights", {})
        self.w_anom = weights.get("anomaly", 0.35)
        self.w_corr = weights.get("correlation", 0.25)
        self.w_patt = weights.get("pattern", 0.25)
        self.w_graph = weights.get("graph", 0.15)

    def generate_leads(
        self,
        features_df: pd.DataFrame,
        anomalies_df: pd.DataFrame,
        correlated_df: pd.DataFrame,
        transactions_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        start_time = time.time()

        if features_df.empty:
            return pd.DataFrame(), {"total_leads_generated": 0}

        # Build correlation lookup map
        corr_map = {}
        if not correlated_df.empty:
            for _, row in correlated_df.iterrows():
                val = float(row.get("correlation_score", 0.0))
                for key_col in ["input_wallet", "output_wallet", "src_ip", "txid"]:
                    k = str(row.get(key_col, ""))
                    if k and k != "UNKNOWN":
                        corr_map[k] = max(corr_map.get(k, 0.0), val)

        # Build anomaly lookup map
        anom_map = {}
        cluster_map = {}
        if not anomalies_df.empty:
            for _, row in anomalies_df.iterrows():
                eid = str(row["entity_id"])
                anom_map[eid] = float(row.get("normalized_anomaly_score", row.get("anomaly_score", 0.0)))
                cluster_map[eid] = int(row.get("cluster_id", -1))

        leads = []
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for idx, feat_row in features_df.iterrows():
            entity_id = str(feat_row["entity_id"])
            entity_type = str(feat_row["entity_type"])

            anom_score = anom_map.get(entity_id, 0.0)
            corr_score = corr_map.get(entity_id, 0.5)
            cluster_id = cluster_map.get(entity_id, -1)

            patterns = self.pattern_detector.detect_patterns_for_entity(entity_id, feat_row.to_dict(), transactions_df)
            pattern_score = min(1.0, len(patterns) * 0.3)

            deg = int(feat_row.get("in_degree", 0)) + int(feat_row.get("out_degree", 0))
            
            # Incorporate new graph heuristics
            pagerank_risk = float(feat_row.get("pagerank_risk", 0.0))
            # Normalize pagerank loosely (assuming it's small, scale it up or cap it)
            pagerank_score = min(1.0, pagerank_risk * 1000)
            
            is_peeling = bool(feat_row.get("is_peeling_chain", False))
            is_coinjoin = bool(feat_row.get("is_coinjoin", False))
            
            if is_peeling or is_coinjoin:
                pattern_score = min(1.0, pattern_score + 0.5)

            graph_score = min(1.0, (deg / 25.0) * 0.5 + pagerank_score * 0.5)

            # Calculate overall priority score [0.0 - 100.0]
            priority_score = round(min(100.0, 100.0 * (
                self.w_anom * anom_score +
                self.w_corr * corr_score +
                self.w_patt * pattern_score +
                self.w_graph * graph_score
            )), 2)

            # Assign Priority Level
            if priority_score >= 85:
                level = "CRITICAL"
            elif priority_score >= 70:
                level = "HIGH"
            elif priority_score >= 40:
                level = "MEDIUM"
            else:
                level = "LOW"

            reasons_list = self.explainability_engine.generate_reasons(
                entity_id, entity_type, anom_score, corr_score, feat_row.to_dict(), patterns
            )

            # Evidence details
            heuristics_str = []
            if is_peeling: heuristics_str.append("Peeling Chain")
            if is_coinjoin: heuristics_str.append("CoinJoin")
            heuristics_info = f" | Patterns: {', '.join(heuristics_str)}" if heuristics_str else ""
            
            evidence_summary = (
                f"Lead ID: LEAD_{idx+1:06d}\n"
                f"Entity ID: {entity_id} ({entity_type.upper()})\n"
                f"Priority Score: {priority_score}/100 [{level}]\n"
                f"Anomaly Score: {anom_score:.4f} | Correlation Score: {corr_score:.4f} | Cluster: {cluster_id}\n"
                f"Degree: {deg} (In: {feat_row.get('in_degree')}, Out: {feat_row.get('out_degree')}) | PageRank Risk: {pagerank_risk:.6f}{heuristics_info}\n"
                f"Volume: {feat_row.get('total_amount_btc', 0.0):.6f} BTC across {feat_row.get('tx_count')} transactions.\n"
                f"Reasons:\n" + "\n".join([f" - {r}" for r in reasons_list])
            )

            if priority_score >= 30 or len(patterns) > 0:
                lead_id_str = f"LEAD_{len(leads)+1:06d}"
                leads.append({
                    "lead_id": lead_id_str,
                    "entity_id": entity_id,
                    "txid": entity_id if entity_type == "txid" else "",
                    "entity_type": entity_type,
                    "priority_score": priority_score,
                    "priority_level": level,
                    "anomaly_score": round(anom_score, 4),
                    "confidence_score": round(corr_score, 4),
                    "cluster_id": cluster_id,
                    "connected_entities_count": deg,
                    "correlated_events_count": 1 if corr_score > 0.5 else 0,
                    "reasons": json.dumps(reasons_list),
                    "supporting_evidence": evidence_summary,
                    "created_at": now_utc
                })

        leads_df = pd.DataFrame(leads)
        if not leads_df.empty:
            leads_df = leads_df.sort_values(by="priority_score", ascending=False).reset_index(drop=True)
            
            # Populate evidence audit records into DuckDB
            try:
                from app.database.duckdb_manager import DuckDBManager
                db = DuckDBManager()
                ev_records = []
                for _, lrow in leads_df.iterrows():
                    ev_records.append({
                        "evidence_id": f"EV_{lrow['lead_id']}",
                        "entity_id": lrow["entity_id"],
                        "entity_type": lrow["entity_type"],
                        "source_file": "synthetic_bitcoin_dataset.csv",
                        "source_record_index": int(lrow["lead_id"].replace("LEAD_", "")),
                        "ingestion_timestamp": lrow["created_at"],
                        "pipeline_stage": "Feature Extraction & Multi-Factor Priority Scoring",
                        "feature_snapshot": json.dumps({
                            "priority_score": lrow["priority_score"],
                            "anomaly_score": lrow["anomaly_score"],
                            "confidence_score": lrow["confidence_score"],
                            "cluster_id": lrow["cluster_id"]
                        }),
                        "correlation_evidence": json.dumps({
                            "connected_entities": lrow["connected_entities_count"],
                            "correlated_events": lrow["correlated_events_count"]
                        }),
                        "model_version": "IsolationForest v1.0 + DBSCAN v1.0",
                        "priority_formula": "Priority = 100 * (0.35*Anomaly + 0.25*Correlation + 0.25*Pattern + 0.15*Graph)",
                        "created_at": lrow["created_at"]
                    })
                db.save_evidence_records(pd.DataFrame(ev_records))
            except Exception:
                pass

        stats = {
            "total_leads_generated": len(leads_df),
            "critical_priority_count": int(np.sum(leads_df["priority_level"] == "CRITICAL")) if not leads_df.empty else 0,
            "high_priority_count": int(np.sum(leads_df["priority_level"] == "HIGH")) if not leads_df.empty else 0,
            "medium_priority_count": int(np.sum(leads_df["priority_level"] == "MEDIUM")) if not leads_df.empty else 0,
            "low_priority_count": int(np.sum(leads_df["priority_level"] == "LOW")) if not leads_df.empty else 0,
            "processing_time_sec": round(time.time() - start_time, 4)
        }

        return leads_df, stats
