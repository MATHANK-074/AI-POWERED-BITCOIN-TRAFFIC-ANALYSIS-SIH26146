# KRISHIGUARD - Investigator Workflow & Operation Guide

## 1. End-to-End Investigation Workflow

```
 ┌────────────────────────────────────────────────────────┐
 │ Step 1: Bulk Ingest Dataset (CSV/JSON/XML)             │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 2: Automatic Schema Mapping & Validation Check    │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 3: Run Network-Blockchain Correlation Engine     │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 4: AI/ML Anomaly Detection & Entity Clustering   │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 5: Explore Interactive Knowledge Graph            │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 6: Review Prioritized Leads & Audit Explanations  │
 └───────────────────────────┬────────────────────────────┘
                             │
 ┌───────────────────────────▼────────────────────────────┐
 │ Step 7: Export Investigation Report (CSV / HTML)       │
 └────────────────────────────────────────────────────────┘
```

---

## 2. Key Investigator Questions Answered

1. **What happened?** Review total transaction counts, volume metrics, and ingestion audit reports on the Overview dashboard.
2. **Which transaction is suspicious?** Filter by high anomaly scores on the Anomaly Explorer page.
3. **Which wallets/entities are connected?** Inspect multi-hop connections on the Cytoscape Investigation Graph.
4. **Is there a relationship between blockchain and network activity?** View correlated candidate IP-to-Wallet linkages and temporal proximity scores.
5. **Why was the transaction flagged?** Read feature-grounded explanation text in the Lead Detail panel.
6. **How risky/suspicious is it?** Check the 0-100 Priority Score and classification levels (CRITICAL, HIGH, MEDIUM, LOW).
7. **Which leads should be investigated first?** Refer to the ranked Investigative Leads list.
