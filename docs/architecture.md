# KRISHIGUARD - System Architecture Specification

## 1. Overview & Operational Model
**KRISHIGUARD** is designed as a zero-internet, completely offline Bitcoin forensic investigation system. It operates locally on Linux distributions (Ubuntu, Debian, Kali, WSL2) to ingest, validate, correlate, cluster, graph, and score cryptocurrency transactions and associated network traffic metadata.

---

## 2. Layered Architecture

```
                               ┌──────────────────────────────────────────┐
                               │  Vite + React + TypeScript + Cytoscape  │
                               │  Investigator Dashboard (Frontend)       │
                               └────────────────────┬─────────────────────┘
                                                    │ REST APIs / OpenAPI
                               ┌────────────────────▼─────────────────────┐
                               │    FastAPI Application (Backend Engine)   │
                               └──────┬──────────────┬──────────────┬─────┘
                                      │              │              │
             ┌────────────────────────┴──┐    ┌──────┴──────┐   ┌───┴───────────────────────┐
             │ Bulk Ingestion & Normalizer│    │ AI / ML     │   │ Knowledge Graph & Leads   │
             │ - CSV / JSON / XML Parsers│    │ Engine      │   │ - NetworkX DiGraph        │
             │ - Schema Mapper           │    │ - IsoForest │   │ - Cytoscape Exporter      │
             │ - Validator & Enrichment  │    │ - K-Means   │   │ - Explainability Engine   │
             └────────────┬──────────────┘    └──────┬──────┘   └───────────┬───────────────┘
                          │                          │                      │
                          └──────────────────────────┼──────────────────────┘
                                                     ▼
                               ┌──────────────────────────────────────────┐
                               │   DuckDB Embedded Analytical Storage     │
                               │   (bitcoin_investigation.duckdb)         │
                               └──────────────────────────────────────────┘
```

### Layer Details:
1. **Frontend Layer**: Built using React 18, Vite, TypeScript (`.tsx`), Tailwind CSS, Recharts, and Cytoscape.js for interactive knowledge graphs.
2. **Backend Services Layer**: FastAPI REST API providing modular endpoints for data ingestion, transaction filtering, entity profiles, anomaly queries, Cytoscape graph exports, model evaluation, and PDF/HTML report exports.
3. **Data Ingestion & Enrichment Layer**: Supports chunked processing of CSV, JSON, JSONL, XML, and Elliptic dataset formats. Performs column mapping, data type coercion, ISO 8601 UTC timestamp standardization, IP validation, duplicate check, and offline enrichment.
4. **Cross-Layer Correlation Engine**: Correlates Network Layer signals (IP, Port, Timestamp, ASN, Geo) with Blockchain Layer signals (TXID, Wallet, Amount, Inputs, Outputs, Fee) using time-window proximity scoring and metadata matching.
5. **AI / ML Anomaly & Clustering Pipeline**: Uses scikit-learn Isolation Forest for anomaly detection, K-Means for entity behavior clustering, StandardScaler for feature scaling, and PCA 2D projections.
6. **Knowledge Graph & Explainability Engine**: Constructs a NetworkX multi-type directed graph (`IP`, `Wallet`, `Transaction`, `Entity`, `ASN`, `Geo`) and generates feature-grounded explanations.
7. **Analytical Database Layer**: Embedded DuckDB engine for high-performance columnar storage and SQL query processing.
