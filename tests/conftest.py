import pytest
import pandas as pd

@pytest.fixture
def sample_transactions_df():
    return pd.DataFrame([
        {
            "txid": "tx_test_001",
            "timestamp": "2026-01-01T10:00:00Z",
            "transaction_timestamp": "2026-01-01T10:00:02Z",
            "src_ip": "192.168.1.100",
            "src_port": 8333,
            "dst_ip": "10.0.0.1",
            "dst_port": 8333,
            "input_wallet": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "output_wallet": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
            "amount_btc": 2.5,
            "fee_btc": 0.0001,
            "synthetic_pattern_label": "normal"
        },
        {
            "txid": "tx_test_002",
            "timestamp": "2026-01-01T10:00:05Z",
            "transaction_timestamp": "2026-01-01T10:00:06Z",
            "src_ip": "192.168.1.100",
            "src_port": 8333,
            "dst_ip": "10.0.0.2",
            "dst_port": 8333,
            "input_wallet": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "output_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "amount_btc": 150.0,
            "fee_btc": 0.05,
            "synthetic_pattern_label": "illicit"
        }
    ])
