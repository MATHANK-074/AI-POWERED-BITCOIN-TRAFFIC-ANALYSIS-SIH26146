# Offline Bitcoin Investigation & AI/ML Analytics System

A complete, high-performance, offline Bitcoin transaction investigation and analytics system designed for financial forensics, network correlation research, and decision support.

The system ingests bulk Bitcoin network-layer and blockchain-layer metadata, correlates network IP observations with blockchain transactions, validates and cleans data, stores it in DuckDB analytical storage, generates graph topologies and ML features, performs anomaly detection and entity clustering, computes transparent investigation priority scores with explainable natural language leads, and provides an offline dashboard with local report exporters.

---

## Key Features

1. **Multi-Format Ingestion**: Supports CSV, JSON (JSON Array & NDJSON), and XML files with chunked parsing.
2. **Validation & Cleaning**: Validates IPv4/IPv6 regex, port ranges (`0 - 65535`), BTC amounts/fees, and timestamps. Logs rejected records to `data/processed/rejected_records.csv`.
3. **DuckDB Local Storage**: Ultra-fast columnar DuckDB database (`data/processed/bitcoin_investigation.duckdb`).
4. **Network-Blockchain Correlation Engine**: Evidence-based temporal window matching ($\pm 1s$ to $\pm 30s$) producing candidate linkages ($\text{IP} \xrightarrow{\text{candidate}} \text{TXID} \rightarrow \text{Wallet}$).
5. **Entity Resolution & Feature Engineering**: Aggregates metrics per wallet and IP (volume, fee ratios, counterparties, in/out ratios, temporal burst scores).
6. **AI/ML Anomaly & Clustering Engine**: Isolation Forest anomaly detection, DBSCAN clustering, PCA 2D scatter projection, and synthetic ground truth evaluation metrics.
7. **NetworkX Knowledge Graph**: Topology builder linking IP, TXID, and Wallet entities with Cytoscape.js export.
8. **Explainable Priority Scoring**: Pattern detectors (Burst, Fan-In, Fan-Out, High-Frequency, Unusual Fee, Network Concentration) combined into a $0-100$ **Investigation Priority Score** with natural language explanations.
9. **Offline React + Tailwind Dashboard**: Interactive Cytoscape graph visualizer, Recharts scatter plots, filterable transaction/wallet/IP/leads explorers, and local report exporters (HTML, JSON, CSV).
10. **Responsible AI Terminology**: Explicit disclaimers ensuring model predictions are decision-support indicators rather than proof of criminal activity.

---

## System Architecture

```
RAW DATA (CSV / JSON / XML)
         │
         ▼
DATA INGESTION & PARSING
         │
         ▼
SCHEMA NORMALIZATION & VALIDATION ──► REJECTED AUDIT LOG
         │
         ▼
DUCKDB ANALYTICAL STORAGE
         │
         ▼
NETWORK-BLOCKCHAIN CORRELATION ENGINE
         │
         ▼
ENTITY RESOLUTION & FEATURE ENGINEERING
         │
         ├──────────────────────────┐
         ▼                          ▼
AI/ML ANOMALY DETECTION    ENTITY CLUSTERING (DBSCAN)
(ISOLATION FOREST)                 │
         │                          │
         └────────────┬─────────────┘
                      ▼
PATTERN DETECTION & EXPLAINABLE LEADS (0-100 SCORES)
                      │
                      ▼
KNOWLEDGE GRAPH CONSTRUCTION (NETWORKX)
                      │
                      ▼
FASTAPI REST BACKEND (http://127.0.0.1:8000)
                      │
                      ▼
OFFLINE REACT + TAILWIND DASHBOARD (http://127.0.0.1:5173)
```

---

## Setup & Running Commands (Windows)

### 1. Environment Setup

```bash
# Clone or open workspace
cd c:\Users\Lenovo\Desktop\Crypto

# Create Python Virtual Environment
python -m venv .venv

# Activate Virtual Environment
.venv\Scripts\activate

# Install Backend Dependencies
pip install -r backend/requirements.txt
pip install python-multipart
```

### 2. Generate Synthetic Dataset (100,000 Records)

```bash
.venv\Scripts\python.exe scripts/generate_dataset.py
```

### 3. Run Batch Processing Pipeline

```bash
.venv\Scripts\python.exe scripts/run_all.py
```

### 4. Start Backend Server (FastAPI)

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

*Interactive API Documentation available at:* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Start Frontend Dashboard (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

*Open Dashboard in Browser:* [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## Unit Testing

Run the automated test suite with pytest:

```bash
.venv\Scripts\python.exe -m pytest backend/tests
```

---

## Responsible Use Disclaimer

This system is designed for educational, research, and analytical decision-support purposes. Model-generated anomaly scores, network correlation linkages, and investigation priority metrics do not by themselves establish criminal conduct, identity, or legal ownership. Human investigator review and corroboration are required.
