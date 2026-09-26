# KRISHIGUARD - Supported Data Formats & Schema Mapping

## 1. Supported Input File Formats
KRISHIGUARD supports offline ingestion of:
- **CSV Files** (`.csv`)
- **JSON Arrays & Nested JSON** (`.json`)
- **Line-Delimited JSON** (`.jsonl`)
- **XML Event Logs** (`.xml`)
- **Elliptic Bitcoin Dataset** (`elliptic_txs_classes.csv`, `elliptic_txs_edgelist.csv`, `elliptic_txs_features.csv`)

---

## 2. Configurable Schema Mapping Dictionary

| Target Schema Field | Accepted Column Aliases in Heterogeneous Datasets |
| :--- | :--- |
| `txid` | `txid`, `transaction_id`, `hash`, `tx_hash`, `tx_id` |
| `timestamp` | `timestamp`, `time`, `datetime`, `tx_time`, `net_timestamp`, `block_time` |
| `src_ip` | `src_ip`, `source_ip`, `ip_src`, `src`, `client_ip`, `sender_ip` |
| `dst_ip` | `dst_ip`, `destination_ip`, `ip_dst`, `dst`, `server_ip`, `target_ip` |
| `src_port` | `src_port`, `source_port`, `port_src`, `sport` |
| `dst_port` | `dst_port`, `destination_port`, `port_dst`, `dport` |
| `input_wallet` | `input_wallet`, `src_wallet`, `sender_wallet`, `from_address`, `vin_address` |
| `output_wallet` | `output_wallet`, `dst_wallet`, `receiver_wallet`, `to_address`, `vout_address` |
| `amount_btc` | `amount_btc`, `amount`, `value`, `value_btc`, `sum_btc` |
| `fee_btc` | `fee_btc`, `fee`, `miner_fee`, `tx_fee` |
