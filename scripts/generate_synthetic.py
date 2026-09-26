import csv
import random
import uuid
from datetime import datetime, timedelta
import faker

fake = faker.Faker()

# Pre-defined set of Geo IPs to simulate realistic locations
GEO_LOCATIONS = [
    {"country": "United States", "asn": "AS7922", "city": "New York"},
    {"country": "Germany", "asn": "AS3320", "city": "Berlin"},
    {"country": "Russia", "asn": "AS12389", "city": "Moscow"},
    {"country": "China", "asn": "AS4134", "city": "Beijing"},
    {"country": "United Kingdom", "asn": "AS2856", "city": "London"},
    {"country": "Netherlands", "asn": "AS1136", "city": "Amsterdam"},
    {"country": "India", "asn": "AS9583", "city": "Mumbai"},
]

def generate_bitcoin_address():
    # Simple mock for Bitcoin addresses (e.g. starting with 1, 3, or bc1)
    prefix = random.choice(['1', '3', 'bc1q'])
    chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    return prefix + ''.join(random.choice(chars) for _ in range(30))

def generate_synthetic_dataset(output_file, num_records=1000):
    print(f"Generating {num_records} synthetic transactions...")
    
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write CSV header as per the SIH requirements
        writer.writerow([
            "timestamp", 
            "src_ip", 
            "dst_ip", 
            "src_port", 
            "dst_port", 
            "txid", 
            "input_addresses", 
            "output_addresses", 
            "input_amounts", 
            "output_amounts", 
            "geo_country", 
            "asn",
            "fee",
            "script_type"
        ])
        
        start_date = datetime.now() - timedelta(days=30)
        
        # Create a small pool of "criminal" wallets to create correlated anomalies
        criminal_wallets = [generate_bitcoin_address() for _ in range(5)]
        
        for i in range(num_records):
            # 5% chance it's part of our 'criminal' cluster
            is_anomaly = random.random() < 0.05
            
            # Timestamp
            tx_time = start_date + timedelta(minutes=random.randint(1, 43200))
            
            # IPs and Geo
            src_ip = fake.ipv4()
            dst_ip = fake.ipv4()
            src_port = random.randint(1024, 65535)
            dst_port = 8333 # standard bitcoin p2p port
            geo = random.choice(GEO_LOCATIONS)
            
            # Transaction ID
            txid = uuid.uuid4().hex
            
            # Generate inputs and outputs (1 to 3 inputs, 1 to 2 outputs)
            num_inputs = random.randint(1, 3)
            num_outputs = random.randint(1, 2)
            
            if is_anomaly:
                input_addrs = [random.choice(criminal_wallets)]
            else:
                input_addrs = [generate_bitcoin_address() for _ in range(num_inputs)]
                
            output_addrs = [generate_bitcoin_address() for _ in range(num_outputs)]
            
            # Amounts (in BTC)
            total_input = round(random.uniform(0.01, 10.0), 4)
            fee = round(random.uniform(0.0001, 0.005), 4)
            total_output = round(total_input - fee, 4)
            
            # Split amounts among inputs and outputs
            input_amounts = [round(total_input / len(input_addrs), 4)] * len(input_addrs)
            output_amounts = [round(total_output / len(output_addrs), 4)] * len(output_addrs)
            
            script_types = ['P2PKH', 'P2SH', 'P2WPKH']
            script_type = random.choice(script_types)
            
            writer.writerow([
                tx_time.isoformat() + "Z",
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                txid,
                "|".join(input_addrs),       # Represent array as | separated string
                "|".join(output_addrs),
                "|".join(map(str, input_amounts)),
                "|".join(map(str, output_amounts)),
                geo["country"],
                geo["asn"],
                fee,
                script_type
            ])
            
    print(f"Dataset successfully saved to {output_file}")

if __name__ == "__main__":
    generate_synthetic_dataset("synthetic_bitcoin_data.csv", 10000)
