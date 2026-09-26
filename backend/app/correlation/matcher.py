from typing import Dict, Any, Optional

class MetadataMatcher:
    """
    Evaluates network metadata correlation signals (IP address, Port, Protocol, ASN, Geo)
    with blockchain transaction attributes.
    """
    def compute_metadata_score(self, record: Dict[str, Any]) -> float:
        score = 0.0
        signals_matched = 0

        # Signal 1: Valid Source IP present
        src_ip = record.get("src_ip")
        if src_ip and str(src_ip).strip() != "" and str(src_ip) != "UNKNOWN":
            score += 0.4
            signals_matched += 1

        # Signal 2: Standard P2P Bitcoin Port (8333 / 18333) or valid port
        src_port = record.get("src_port")
        dst_port = record.get("dst_port")
        if src_port in [8333, 18333, 8332] or dst_port in [8333, 18333, 8332]:
            score += 0.3
            signals_matched += 1
        elif src_port or dst_port:
            score += 0.1

        # Signal 3: Protocol match
        protocol = str(record.get("protocol", "")).lower()
        if "btc" in protocol or "p2p" in protocol or "bitcoin" in protocol:
            score += 0.3
            signals_matched += 1

        return round(min(1.0, score), 4)
