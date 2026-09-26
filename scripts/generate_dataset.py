import os
import json
import random
import hashlib
import time
import datetime
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET
try:
    import geoip2.database
except ImportError:
    geoip2 = None

# Ensure deterministic yet diverse generation
random.seed(42)

# Bitcoin Address Generators
def generate_p2pkh_address():
    chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return "1" + "".join(random.choices(chars, k=33))

def generate_p2sh_address():
    chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return "3" + "".join(random.choices(chars, k=33))

def generate_bech32_address():
    chars = "023456789acdefghjklmnpqrstuvwxyz"
    return "bc1q" + "".join(random.choices(chars, k=38))

def generate_wallet_address():
    rand = random.random()
    if rand < 0.6:
        return generate_bech32_address()
    elif rand < 0.85:
        return generate_p2pkh_address()
    else:
        return generate_p2sh_address()

def generate_txid(index):
    raw = f"tx_{index}_{random.randint(100000, 999999)}_{time.time()}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def generate_ip():
    # Mix of private/public ranges for realism
    rand = random.random()
    if rand < 0.3:
        return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    elif rand < 0.5:
        return f"10.{random.randint(0, 255)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
    else:
        return f"{random.randint(11, 220)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

SCRIPT_TYPES = ["p2pkh", "p2sh", "p2wpkh", "p2tr"]

def generate_synthetic_dataset(num_records=100000, output_dir="data/synthetic"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {num_records:,} synthetic Bitcoin transaction records with network layer correlation...")
    
    # Pre-generate pool of wallets & IPs to build realistic graph topologies
    num_entities = max(1000, num_records // 50)
    wallet_pool = [generate_wallet_address() for _ in range(num_entities)]
    ip_pool = [generate_ip() for _ in range(num_entities // 2)]
    
    start_time = datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    
    city_reader = None
    asn_reader = None
    if geoip2:
        try:
            city_reader = geoip2.database.Reader("data/GeoLite2-City.mmdb")
            asn_reader = geoip2.database.Reader("data/GeoLite2-ASN.mmdb")
        except FileNotFoundError:
            print("MaxMind DBs not found. Proceeding without offline GeoIP.")
    
    records = []

    # Patterns distribution
    # 70% Normal, 5% Burst, 5% Fan-In, 5% Fan-Out, 5% High-Freq, 5% Unusual Fee, 5% Cyclic
    
    # Pre-define specific entities for specific behavioral patterns
    burst_wallet = random.choice(wallet_pool)
    burst_ip = random.choice(ip_pool)
    
    fan_in_target_wallet = random.choice(wallet_pool)
    fan_out_source_wallet = random.choice(wallet_pool)
    
    high_freq_wallet = random.choice(wallet_pool)
    high_freq_ip = random.choice(ip_pool)
    
    cyclic_wallets = [generate_wallet_address() for _ in range(4)]
    
    for i in range(num_records):
        pattern_roll = random.random()
        
        # Base timestamps
        time_offset_seconds = random.randint(0, 86400 * 30) # Spread over 30 days
        tx_dt = start_time + datetime.timedelta(seconds=time_offset_seconds)
        
        # Default network delta: within +- 3 seconds
        net_delta = random.uniform(-3.0, 3.0)
        net_dt = tx_dt + datetime.timedelta(seconds=net_delta)
        
        tx_iso = tx_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        net_iso = net_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        src_ip = random.choice(ip_pool)
        dst_ip = random.choice(ip_pool)
        src_port = random.randint(1024, 65535)
        dst_port = 8333 # Standard Bitcoin P2P port
        
        input_wallet = random.choice(wallet_pool)
        output_wallet = random.choice(wallet_pool)
        while output_wallet == input_wallet:
            output_wallet = random.choice(wallet_pool)
            
        amount_btc = round(random.expovariate(2.0) + 0.001, 8)
        fee_btc = round(amount_btc * random.uniform(0.0001, 0.005) + 0.00001, 8)
        script_type = random.choice(SCRIPT_TYPES)
        block_height = 850000 + (time_offset_seconds // 600) # Avg 10 mins per block
        
        entity_id = f"ENT_{random.randint(100, 999)}"
        behavior_type = "normal"
        pattern_label = "normal_activity"
        
        # Apply specific pattern logic
        if pattern_roll > 0.95:
            # Burst pattern
            behavior_type = "burst"
            pattern_label = "burst_activity"
            input_wallet = burst_wallet
            src_ip = burst_ip
            # Fixed timestamp window
            burst_dt = start_time + datetime.timedelta(days=10, seconds=random.randint(0, 120))
            tx_iso = burst_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            net_iso = (burst_dt + datetime.timedelta(seconds=random.uniform(-1, 1))).strftime("%Y-%m-%dT%H:%M:%SZ")
            entity_id = "ENT_BURST_01"
            
        elif pattern_roll > 0.90:
            # Fan-In pattern
            behavior_type = "fan_in"
            pattern_label = "fan_in_aggregation"
            output_wallet = fan_in_target_wallet
            entity_id = "ENT_FANIN_01"
            
        elif pattern_roll > 0.85:
            # Fan-Out pattern
            behavior_type = "fan_out"
            pattern_label = "fan_out_distribution"
            input_wallet = fan_out_source_wallet
            entity_id = "ENT_FANOUT_01"
            
        elif pattern_roll > 0.80:
            # High-Frequency pattern
            behavior_type = "high_frequency"
            pattern_label = "high_frequency_trader"
            input_wallet = high_freq_wallet
            src_ip = high_freq_ip
            entity_id = "ENT_HF_01"
            
        elif pattern_roll > 0.75:
            # Unusual Fee pattern
            behavior_type = "unusual_fee"
            pattern_label = "high_fee_anomaly"
            fee_btc = round(amount_btc * random.uniform(0.15, 0.5), 8) # Extremely high fee ratio
            entity_id = "ENT_FEE_01"
            
        elif pattern_roll > 0.70:
            # Cyclic pattern
            behavior_type = "cyclic"
            pattern_label = "cyclic_flow"
            idx = i % len(cyclic_wallets)
            input_wallet = cyclic_wallets[idx]
            output_wallet = cyclic_wallets[(idx + 1) % len(cyclic_wallets)]
            entity_id = "ENT_CYCLIC_01"

        def get_geo(ip):
            geo = {"country": "UNKNOWN", "city": "UNKNOWN", "lat": 0.0, "lon": 0.0, "asn": "UNKNOWN"}
            if city_reader:
                try:
                    resp = city_reader.city(ip)
                    geo["country"] = resp.country.iso_code or "UNKNOWN"
                    geo["city"] = resp.city.name or "UNKNOWN"
                    geo["lat"] = resp.location.latitude or 0.0
                    geo["lon"] = resp.location.longitude or 0.0
                except:
                    pass
            if asn_reader:
                try:
                    resp = asn_reader.asn(ip)
                    geo["asn"] = f"AS{resp.autonomous_system_number}" if resp.autonomous_system_number else "UNKNOWN"
                except:
                    pass
            return geo

        src_geo = get_geo(src_ip)
        dst_geo = get_geo(dst_ip)

        records.append({
            "timestamp": net_iso,
            "src_ip": src_ip,
            "src_port": src_port,
            "dst_ip": dst_ip,
            "dst_port": dst_port,
            "src_country": src_geo["country"],
            "src_city": src_geo["city"],
            "src_lat": src_geo["lat"],
            "src_lon": src_geo["lon"],
            "src_asn": src_geo["asn"],
            "dst_country": dst_geo["country"],
            "dst_city": dst_geo["city"],
            "dst_lat": dst_geo["lat"],
            "dst_lon": dst_geo["lon"],
            "dst_asn": dst_geo["asn"],
            "network_event_id": f"NET_{i+1:08d}",
            "protocol": "btc_p2p",
            "txid": generate_txid(i),
            "input_wallet": input_wallet,
            "output_wallet": output_wallet,
            "amount_btc": amount_btc,
            "fee_btc": fee_btc,
            "script_type": script_type,
            "block_height": int(block_height),
            "transaction_timestamp": tx_iso,
            "synthetic_entity_id": entity_id,
            "synthetic_behavior_type": behavior_type,
            "synthetic_pattern_label": pattern_label
        })

    df = pd.DataFrame(records)
    
    # Save CSV primary dataset
    csv_file = out_path / "synthetic_bitcoin_dataset.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved synthetic CSV dataset to {csv_file} ({os.path.getsize(csv_file) / (1024*1024):.2f} MB)")
    
    # Save sample JSON and XML files for multi-format ingestion testing (1,000 records each)
    json_file = out_path / "sample_dataset.json"
    jsonl_file = out_path / "sample_dataset.jsonl"
    xml_file = out_path / "sample_dataset.xml"
    
    sample_records = records[:1000]
    
    # Write JSON Array
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sample_records, f, indent=2)
        
    # Write JSON Lines
    with open(jsonl_file, "w", encoding="utf-8") as f:
        for rec in sample_records:
            f.write(json.dumps(rec) + "\n")
            
    # Write XML
    root = ET.Element("bitcoin_transactions")
    for rec in sample_records:
        tx_elem = ET.SubElement(root, "transaction")
        for key, val in rec.items():
            child = ET.SubElement(tx_elem, key)
            child.text = str(val)
    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    
    print(f"Saved sample JSON, JSONL, and XML datasets for format validation testing.")
    return csv_file

if __name__ == "__main__":
    generate_synthetic_dataset(num_records=100000)
