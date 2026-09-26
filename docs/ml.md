# KRISHIGUARD - AI / ML Methodology & Feature Engineering

## 1. Feature Engineering Vector
KRISHIGUARD computes a 12-dimensional feature vector for every wallet address and IP network entity:

| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `tx_count` | Integer | Total count of observed transactions |
| `total_amount_btc` | Float | Cumulative total Bitcoin volume transferred |
| `avg_amount_btc` | Float | Average transaction amount in BTC |
| `max_amount_btc` | Float | Maximum single transaction amount in BTC |
| `min_amount_btc` | Float | Minimum single transaction amount in BTC |
| `avg_fee_btc` | Float | Average miner fee paid |
| `unique_ip_count` | Integer | Count of distinct IP addresses observed |
| `unique_counterparties` | Integer | Count of unique input/output counterparties |
| `in_degree` | Integer | Graph in-degree (incoming transactions) |
| `out_degree` | Integer | Graph out-degree (outgoing transactions) |
| `in_out_ratio` | Float | Ratio of in-degree to out-degree |
| `burst_score` | Float | Fraction of transactions occurring within 10s window |

---

## 2. Machine Learning Pipeline

### 2.1 Feature Scaling (`StandardScaler`)
Features are standardized using `sklearn.preprocessing.StandardScaler`:
$$z = \frac{x - \mu}{\sigma}$$

### 2.2 Anomaly Detection (`IsolationForest`)
- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Parameters**: `contamination=0.05`, `n_estimators=100`, `random_state=42`.
- **Output Score**: Raw decision function is normalized to $[0.0, 1.0]$ where $1.0$ indicates extreme anomaly.

### 2.3 Entity Clustering (`KMeans` & `PCA`)
- **Algorithm**: `sklearn.cluster.KMeans` ($k=5$)
- **Dimensionality Reduction**: `sklearn.decomposition.PCA(n_components=2)` for 2D UI cluster scatter plotting.
- **Evaluation**: Silhouette Score and cluster size distribution.

---

## 3. Priority Lead Scoring Formula
Investigation Priority Score ($S \in [0, 100]$):
$$S = \min\left(100, 100 \times \left( w_{\text{anom}} A + w_{\text{corr}} C + w_{\text{patt}} P + w_{\text{graph}} G \right)\right)$$

Where:
- $w_{\text{anom}} = 0.35$ (Anomaly Score $A$)
- $w_{\text{corr}} = 0.25$ (Network Correlation Score $C$)
- $w_{\text{patt}} = 0.25$ (Pattern Indicator Score $P$)
- $w_{\text{graph}} = 0.15$ (Graph Topology Score $G$)
