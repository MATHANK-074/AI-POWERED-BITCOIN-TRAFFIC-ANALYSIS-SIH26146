import math
from typing import Dict, Any, Optional
import pandas as pd

import numpy as np

class OfflineEnricher:
    """
    Offline data enrichment module.
    Annotates data records with country, city, ASN, network metadata, and derived features.
    If real enrichment metadata is unavailable, explicitly labels fields as 'UNKNOWN'
    or marks dataset provenance as 'REAL DATA', 'DERIVED DATA', 'UNKNOWN DATA', or 'SYNTHETIC/DEMO DATA'.
    """
    def __init__(self, geoip_db_path: Optional[str] = None):
        self.geoip_db_path = geoip_db_path

    def enrich_dataframe(self, df: pd.DataFrame, is_synthetic: bool = False) -> pd.DataFrame:
        if df.empty:
            return df

        enriched_df = df.copy()

        # 1. Data Provenance Tagging
        if "synthetic_entity_id" in enriched_df.columns or is_synthetic:
            enriched_df["data_provenance"] = "SYNTHETIC/DEMO DATA"
        else:
            enriched_df["data_provenance"] = "REAL DATA"

        # 2. Network Metadata Enrichment (Country, City, ASN, Lat, Lon)
        try:
            import geoip2.database
            has_geoip = True
        except ImportError:
            has_geoip = False

        city_reader = None
        asn_reader = None
        if has_geoip:
            try:
                city_reader = geoip2.database.Reader("data/GeoLite2-City.mmdb")
                asn_reader = geoip2.database.Reader("data/GeoLite2-ASN.mmdb")
            except FileNotFoundError:
                pass

        def get_geo_info(ip):
            res = {"country": "UNKNOWN", "city": "UNKNOWN", "lat": 0.0, "lon": 0.0, "asn": "UNKNOWN"}
            if not isinstance(ip, str): return res
            if city_reader:
                try:
                    c = city_reader.city(ip)
                    res["country"] = c.country.iso_code or "UNKNOWN"
                    res["city"] = c.city.name or "UNKNOWN"
                    res["lat"] = c.location.latitude or 0.0
                    res["lon"] = c.location.longitude or 0.0
                except: pass
            if asn_reader:
                try:
                    a = asn_reader.asn(ip)
                    res["asn"] = f"AS{a.autonomous_system_number}" if a.autonomous_system_number else "UNKNOWN"
                except: pass
            return res

        if "src_ip" in enriched_df.columns:
            geo_series = enriched_df["src_ip"].apply(get_geo_info)
            if "src_country" not in enriched_df.columns:
                enriched_df["src_country"] = geo_series.apply(lambda x: x["country"])
            if "src_city" not in enriched_df.columns:
                enriched_df["src_city"] = geo_series.apply(lambda x: x["city"])
            if "src_lat" not in enriched_df.columns:
                enriched_df["src_lat"] = geo_series.apply(lambda x: x["lat"])
            if "src_lon" not in enriched_df.columns:
                enriched_df["src_lon"] = geo_series.apply(lambda x: x["lon"])
            if "src_asn" not in enriched_df.columns:
                enriched_df["src_asn"] = geo_series.apply(lambda x: x["asn"])

        if "dst_ip" in enriched_df.columns:
            geo_series = enriched_df["dst_ip"].apply(get_geo_info)
            if "dst_country" not in enriched_df.columns:
                enriched_df["dst_country"] = geo_series.apply(lambda x: x["country"])
            if "dst_city" not in enriched_df.columns:
                enriched_df["dst_city"] = geo_series.apply(lambda x: x["city"])
            if "dst_lat" not in enriched_df.columns:
                enriched_df["dst_lat"] = geo_series.apply(lambda x: x["lat"])
            if "dst_lon" not in enriched_df.columns:
                enriched_df["dst_lon"] = geo_series.apply(lambda x: x["lon"])
            if "dst_asn" not in enriched_df.columns:
                enriched_df["dst_asn"] = geo_series.apply(lambda x: x["asn"])

        for col in ["country", "city", "asn"]:
            if col not in enriched_df.columns:
                enriched_df[col] = enriched_df.get("src_" + col, "UNKNOWN")
            else:
                enriched_df[col] = enriched_df[col].fillna("UNKNOWN")

        # 3. Timestamp Derived Features
        for ts_col in ["timestamp", "transaction_timestamp"]:
            if ts_col in enriched_df.columns:
                dt_series = pd.to_datetime(enriched_df[ts_col], errors="coerce", utc=True)
                enriched_df[f"{ts_col}_hour"] = dt_series.dt.hour.fillna(-1).astype(int)
                enriched_df[f"{ts_col}_dayofweek"] = dt_series.dt.dayofweek.fillna(-1).astype(int)
                enriched_df[f"{ts_col}_is_weekend"] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)

        # 4. Transaction Derived Features
        if "amount_btc" in enriched_df.columns:
            amt = enriched_df["amount_btc"].fillna(0.0)
            fee = enriched_df["fee_btc"].fillna(0.0) if "fee_btc" in enriched_df.columns else pd.Series(0.0, index=df.index)
            enriched_df["fee_to_amount_ratio"] = (fee / (amt + 1e-8)).round(6)
            enriched_df["amount_log"] = np.log1p(amt).round(4)

        return enriched_df
