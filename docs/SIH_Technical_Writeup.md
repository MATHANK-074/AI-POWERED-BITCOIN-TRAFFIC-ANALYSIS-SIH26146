# Technical Write-Up: AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

## 1. Architectural Approach
Our solution provides a completely offline, end-to-end pipeline designed specifically for Linux environments (via Docker Compose) to ensure security and operability in isolated environments. 

The architecture consists of four main layers:
1. **Data Ingestion & Normalization:** Highly concurrent chunked parsing of CSV, JSON, and XML metadata using Python. Validated data is stored in a columnar **DuckDB** database for ultra-fast, offline analytical queries without the overhead of a traditional RDBMS.
2. **Network-Blockchain Correlation:** A deterministic temporal window matching engine (±1s to ±30s) that correlates IP observations (Network Layer) with TXIDs (Blockchain Layer), producing candidate linkages.
3. **AI/ML & Graph Engine:** This core engine extracts entity features, runs unsupervised clustering, builds a NetworkX knowledge graph, and applies deterministic heuristics for laundering patterns.
4. **Presentation Layer:** An offline React + Tailwind CSS dashboard that provides graph link-analysis (Cytoscape.js) and prioritized alerts for investigators.

## 2. Model Choice Justification
We adopted a hybrid AI/ML approach combining unsupervised learning and graph theory:

- **Isolation Forest (Anomaly Detection):** Chosen over SVM or Neural Networks because financial crime data is highly imbalanced and lacks labeled ground truth. Isolation Forests are computationally efficient (O(n log n)) and excel at isolating statistically unusual volumetric flows (e.g., massive fee spikes or transaction bursts) without needing labeled training data.
- **DBSCAN (Entity Clustering):** Chosen over K-Means because cybercriminal syndicates operate in non-spherical, dense clusters of varying sizes. DBSCAN organically finds these dense groups based on structural behavior without needing a predefined number of clusters ($k$).
- **Personalized PageRank (Risk Propagation):** Standard PageRank measures importance, but *Personalized* PageRank allows us to seed known illicit wallets and probabilistically propagate their "taint" scores through the network to flag accomplices.

## 3. Explainability Method (XAI)
A critical requirement for intelligence and law enforcement is that AI models cannot be "black boxes." We achieve explainability through a **Multi-Factor Rule Engine combined with SHAP-inspired logic**:

When a wallet or transaction is flagged with a high Confidence Score (0-100), the system generates a natural language "Explainable Lead" by tracing back which features contributed to the anomaly:
- *Fan-In / Fan-Out Ratios:* Explains if a wallet is acting as a collection node or distribution node.
- *Deterministic Laundering Flags:* Explicitly tags nodes involved in "Peeling Chains" or "CoinJoin" structures.
- *Proximity to Threat Seeds:* Explains the node's Personalized PageRank risk score relative to known illicit seeds.

This ensures that human investigators receive actionable intelligence (e.g., *"Flagged due to involvement in a peeling chain and high proximity to a known illicit seed"*) rather than just a raw probability score.
