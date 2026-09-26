<div align="center">
  <img src="https://img.shields.io/badge/Status-SIH%20Ready-success" alt="Status" />
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue" alt="Platform" />
  <img src="https://img.shields.io/badge/AI_Model-Isolation%20Forest%20%2B%20DBSCAN-purple" alt="AI Models" />
  <h1>🛡️ KRISHIGUARD</h1>
  <h3>AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic</h3>
  <h4>National Technical Research Organisation (NTRO) - Problem Statement 5</h4>
</div>

---

## 📖 Overview
**KRISHIGUARD** is a complete, 100% offline digital forensics platform designed to meet the exact requirements of Problem Statement 5. It ingests bulk Bitcoin transaction/network metadata, correlates network-layer observations (IP/port/timing) with blockchain-layer data (wallet/TXID/amount), and deploys unsupervised AI/ML models to detect anomalies, cluster entities, and generate prioritized, explainable investigative leads. 

Designed specifically to address the challenge of tracking illicit funds (ransomware, darknet proceeds) through pseudonymous, peer-to-peer networks without relying on external cloud APIs.

---

## 🎯 Challenge Objectives Met
- ✅ **Bulk Ingestion:** Parses massive metadata datasets (timestamp, IP, port, TXID, wallets, amounts, fees).
- ✅ **Graph Construction:** Builds an entity/transaction knowledge graph linking IPs, wallets, and transactions.
- ✅ **AI/ML Detection:** Deploys working ML models (Isolation Forest, DBSCAN) for anomaly detection and clustering—not just rules.
- ✅ **Explainable Alerts:** Generates a ranked alert list with confidence scores and clear human-readable evidence for why entities were flagged.
- ✅ **Dashboard Visualization:** Presents findings via a comprehensive dashboard and interactive link-analysis graph.
- ✅ **Offline Linux Solution:** Fully workable offline solution for Linux platforms (Docker & Bash).

---

## 🚀 Deployment (Linux / Debian / Ubuntu)

The platform is designed to be evaluated flawlessly on a Linux environment without any complex setup. You can deploy it using either the native bash script or Docker Compose.

### Option 1: Native Execution (Bash Script)
If you have Node.js and Python installed, you can use the automated launch script to install dependencies and run both servers instantly.

1. Open your terminal in the repository root.
2. Grant execution permissions:
   ```bash
   chmod +x START_KRISHIGUARD_LINUX.sh
   ```
3. Run the launcher:
   ```bash
   ./START_KRISHIGUARD_LINUX.sh
   ```
*The script will configure the Python environment, install frontend dependencies, boot the servers in parallel, and expose the UI at `http://127.0.0.1:5173`.*

### Option 2: Docker Compose (Fully Containerized & Offline)
For a true 100% isolated offline evaluation without installing language dependencies, use the provided Docker configuration.

1. Open your terminal in the repository root.
2. Run the compose command:
   ```bash
   docker-compose up --build
   ```
*Docker will build and network the frontend and backend containers. Once running, access the dashboard at `http://127.0.0.1:5173`.*

---

## 🎲 Generating Synthetic Data (Dataset Compliance)
To evaluate the platform, you can generate a synthetic dataset modeled on real Bitcoin P2P/transaction fields. The generator creates the exact required minimum fields: `timestamp`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `txid`, `input_addresses[]`, `output_addresses[]`, `input_amounts[]`, `output_amounts[]`, `geo_country/asn` (using offline GeoIP).

```bash
# Ensure you are in your python virtual environment
pip install faker
python scripts/generate_synthetic.py
```
*This will create a `synthetic_bitcoin_data.csv` file ready to be uploaded in the Data Ingestion tab.*

---

## 🧠 Technical Write-Up: Approach & AI Methodology

### 1. Architectural Approach
Our solution implements a multi-stage pipeline designed for offline, high-throughput execution:
* **Multi-format Data Ingestion:** Custom parsers for CSV, JSON, and XML ingest raw metadata directly into a **DuckDB** analytical datastore. DuckDB was chosen for its blazing-fast, serverless, in-memory OLAP capabilities.
* **Network-Blockchain Correlation:** A time-window correlation engine links observed network IPs and Ports to specific Bitcoin Wallets and Transactions, bridging the gap between physical infrastructure and blockchain activity.
* **Knowledge Graph Construction:** We map these correlations into a mathematical graph (analyzed via `NetworkX` and visualized via `Cytoscape.js`), extracting vital topological heuristics like **Degree Centrality** and **Betweenness**.

### 2. AI/ML Model Choice
We directly address the suggested AI/ML focus areas using advanced models:
* **Entity Clustering (DBSCAN):** A density-based spatial clustering algorithm used to group wallets likely owned by one entity using common-input-ownership and graph correlations. It natively handles "noise" to identify dense criminal rings without needing a predefined cluster count.
* **Anomaly Detection (Isolation Forest):** Used to flag statistically unusual transactions/flows. It isolates high-dimensional outliers (e.g., wallets with unusually high transaction frequencies or massive fee spikes) without requiring a labeled training dataset.
* **Peeling-Chain / Mixing Detection & Risk Scoring:** Graph algorithms propagate risk scores from anomalous nodes across the network, automatically identifying laundering-pattern transaction sequences (peeling chains, CoinJoin-like structures) by analyzing input/output fan-out patterns.

### 3. Explainability Method (XAI)
A critical requirement is that investigators must trust the AI. Our `PriorityScorer` fuses the ML outputs (Isolation Forest anomaly scores) with Graph Heuristics to generate **Ranked, Explainable Leads**.
* **Confidence Scoring:** Each lead is assigned a mathematically derived 0-100 Confidence Score based on the severity of the anomaly and the density of the entity's cluster.
* **Audit Trail Generation:** Instead of a "black box" alert, the system generates human-readable reasons for every flag (e.g., *"Flagged due to top 5% transaction volume"* or *"Directly connected to 3 anomalous IP addresses"*). This is displayed directly on the UI's **Explainability Panel**.

---

## 🖥️ UI & Dashboard Features

The frontend is a custom-built, responsive React application styled as a premium Dark-Mode Forensic Workstation:

* **Command Center:** Real-time metrics, anomaly detection rates, and a geographical IP map.
* **Forensic Data Tables:** Deep-dive tabular views into Transactions, Priority Leads, and Case Management with intelligent sorting and filtering.
* **Interactive Investigation Graph:** A dynamic, physics-based (`cose`) link-analysis visualization where users can trace funds across Wallets (Purple Diamonds), IPs (Cyan Hexagons), and TXIDs (Blue Circles).

---
*Developed for the Smart India Hackathon (SIH).*
