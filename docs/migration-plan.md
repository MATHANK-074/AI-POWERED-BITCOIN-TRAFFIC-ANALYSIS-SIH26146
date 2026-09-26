# KRISHIGUARD - Migration & System Enhancement Plan

## 1. Executive Summary
This document outlines the refactoring and feature enhancement plan for **KRISHIGUARD – AI-Powered Offline Bitcoin Investigation System**. The objective is to preserve all existing working backend services, FastAPI endpoints, ML pipelines, and React dashboard components, while implementing all missing SIH features, case management, evidence audit trail, Parquet/Elliptic dataset support, and Linux cross-platform compliance.

---

## 2. Assessment of Existing Architecture

### 2.1 Preserved Working Components
- **FastAPI REST Server**: Backend routing in `backend/app/api/` (`transactions.py`, `entities.py`, `anomalies.py`, `graph.py`, `leads.py`, `evaluation.py`, `health.py`, `reports.py`).
- **DuckDB Analytical Engine**: Columns indexed columnar storage in `backend/app/database/duckdb_manager.py`.
- **Machine Learning Core**: Isolation Forest anomaly scoring (`backend/app/ml/anomaly_detection.py`), K-Means clustering (`backend/app/ml/clustering.py`), and `StandardScaler` feature scaling.
- **NetworkX Graph Analysis**: DiGraph builder in `backend/app/graph/builder.py` and Cytoscape exporter in `backend/app/graph/export.py`.
- **Explainability & Lead Scoring**: Feature-based rule engine in `backend/app/explainability/` and `backend/app/leads/`.
- **React + Tailwind Frontend**: Investigator UI pages in `frontend/src/pages/` (`Overview`, `Transactions`, `Entities`, `Anomalies`, `Clusters`, `Leads`, `InvestigationGraph`, `DataIngestion`, `Evaluation`, `SystemLogs`).

### 2.2 System Enhancements & Added Features
1. **Evidence & Audit Trail Module**:
   - New database table `evidence_audit_trail` and endpoint `/api/evidence/{entity_id}`.
   - Traceability payload: Source file name, row/record index, timestamp, ingestion stage, feature vector snapshot, correlation signals, model version, and priority scoring formula.
   - Integrated Evidence Panel UI component (`frontend/src/components/EvidencePanel.tsx`).
2. **Investigation Case Management**:
   - New database table `investigation_cases` and API endpoints `/api/cases` (GET, POST, PUT, DELETE, Export).
   - Allows investigators to group suspicious transactions, wallets, and leads under a case ID with notes, status (`OPEN`, `UNDER INVESTIGATION`, `RESOLVED`, `ARCHIVED`), and export case reports.
   - Integrated Case Management Page (`frontend/src/pages/Cases.tsx`).
3. **Parquet & Elliptic Dataset Processing**:
   - Dedicated parser `backend/app/ingestion/elliptic.py` for `elliptic_txs_classes.csv`, `elliptic_txs_edgelist.csv`, `elliptic_txs_features.csv`.
   - Native PyArrow / DuckDB Parquet ingestion support (`backend/app/ingestion/parquet_parser.py`).
4. **Enhanced Data Enrichment & Provenance**:
   - Offline GeoIP/ASN enrichment with explicit data source classification (`REAL`, `DERIVED`, `UNKNOWN`, `SYNTHETIC`).
5. **Cross-Layer Correlation Engine**:
   - Multi-signal scoring between network observations (IP, Port, Timestamp, ASN) and blockchain layer (TXID, Wallet, Amount, Fee).
   - Graceful fallback: Displays `"Network evidence unavailable"` when network data is not present (no invented data).
6. **Cytoscape Graph Enhancements**:
   - Path search, neighbor expansion, suspicious cluster highlighting, and node/edge inspection drawer.
7. **Demo / Synthetic Data UI Banner**:
   - Header badge clearly indicating when synthetic demo data is loaded vs live datasets.
8. **Linux Deployment & Shell Scripts**:
   - POSIX-compliant `setup.sh`, `start.sh`, `stop.sh` scripts, relative `pathlib.Path` paths, zero Windows-only dependencies.
9. **SIH Requirement Matrix**:
   - Full mapping documented in `docs/sih-requirement-matrix.md`.

---

## 3. Targeted Modular Structure

```
KRISHIGUARD/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── ingestion.py
│   │   │   ├── transactions.py
│   │   │   ├── entities.py
│   │   │   ├── graph.py
│   │   │   ├── anomalies.py
│   │   │   ├── leads.py
│   │   │   ├── cases.py            <-- NEW: Case Management API
│   │   │   ├── evidence.py         <-- NEW: Evidence Audit Trail API
│   │   │   ├── evaluation.py
│   │   │   ├── health.py
│   │   │   └── reports.py
│   │   ├── ingestion/
│   │   │   ├── csv_parser.py
│   │   │   ├── json_parser.py
│   │   │   ├── xml_parser.py
│   │   │   ├── parquet_parser.py   <-- NEW: Parquet Parser
│   │   │   ├── elliptic.py         <-- NEW: Elliptic Dataset Ingest
│   │   │   ├── validator.py
│   │   │   ├── normalizer.py
│   │   │   └── enrichment.py
│   │   ├── correlation/
│   │   │   ├── network_blockchain.py
│   │   │   ├── temporal.py
│   │   │   └── matcher.py
│   │   ├── features/
│   │   │   ├── feature_engineering.py
│   │   │   ├── transaction_features.py
│   │   │   ├── wallet_features.py
│   │   │   └── network_features.py
│   │   ├── ml/
│   │   │   ├── anomaly_detection.py
│   │   │   ├── clustering.py
│   │   │   └── evaluation.py
│   │   ├── graph/
│   │   │   ├── builder.py
│   │   │   ├── analysis.py
│   │   │   └── export.py
│   │   ├── explainability/
│   │   │   ├── reasons.py
│   │   │   └── lead_generator.py
│   │   └── database/
│   │       └── duckdb_manager.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── EvidencePanel.tsx   <-- NEW: Evidence Traceability UI
│   │   │   └── CaseModal.tsx       <-- NEW: Case Creation Modal
│   │   ├── pages/
│   │   │   ├── Overview.tsx
│   │   │   ├── Transactions.tsx
│   │   │   ├── Entities.tsx
│   │   │   ├── Anomalies.tsx
│   │   │   ├── Clusters.tsx
│   │   │   ├── Leads.tsx
│   │   │   ├── Cases.tsx           <-- NEW: Case Management Page
│   │   │   ├── InvestigationGraph.tsx
│   │   │   ├── DataIngestion.tsx
│   │   │   └── Evaluation.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── App.tsx
├── docs/
│   ├── current-system-audit.md
│   ├── migration-plan.md
│   ├── sih-requirement-matrix.md
│   ├── architecture.md
│   ├── ml.md
│   └── investigation-flow.md
├── scripts/
│   ├── run_all.py
│   ├── generate_dataset.py
│   └── ingest_elliptic.py
├── setup.sh
├── start.sh
├── stop.sh
└── README.md
```

---

## 4. Phased Implementation Roadmap

- **Phase 1: Database & Core APIs**: Add `investigation_cases` and `evidence_audit_trail` tables to DuckDB schema. Implement `/api/cases` and `/api/evidence` REST routes.
- **Phase 2: Ingestion, Parquet & Elliptic Dataset Support**: Implement `parquet_parser.py` and `elliptic.py` for bulk dataset processing.
- **Phase 3: Graph Engine & Path Analysis**: Add NetworkX graph traversal (neighbor search, shortest path, connected components, suspicious node detection).
- **Phase 4: Frontend UI Enhancement**: Add `Cases.tsx`, `EvidencePanel.tsx`, global multi-attribute search, filter drawer, and Demo Data banner in `Navbar.tsx`.
- **Phase 5: Linux Compatibility & Verification**: Audit POSIX scripts (`setup.sh`, `start.sh`, `stop.sh`), run `pytest` test suite, update `docs/sih-requirement-matrix.md`, and verify end-to-end functionality.
