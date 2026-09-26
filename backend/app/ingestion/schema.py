from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BitcoinRecord(BaseModel):
    timestamp: str = Field(..., description="Network observation timestamp (ISO format)")
    src_ip: str = Field(..., description="Source IP address")
    src_port: int = Field(..., ge=0, le=65535, description="Source port number")
    dst_ip: str = Field(..., description="Destination IP address")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination port number")
    txid: str = Field(..., description="Bitcoin Transaction ID (hash)")
    input_wallet: str = Field(..., description="Sender wallet address")
    output_wallet: str = Field(..., description="Recipient wallet address")
    amount_btc: float = Field(..., ge=0, description="Amount transferred in BTC")
    fee_btc: float = Field(..., ge=0, description="Transaction miner fee in BTC")
    script_type: str = Field(default="p2wpkh", description="Bitcoin script type")
    block_height: Optional[int] = Field(default=None, description="Blockchain block height")
    protocol: Optional[str] = Field(default="btc_p2p", description="Network protocol")
    network_event_id: Optional[str] = Field(default=None, description="Unique network event ID")
    transaction_timestamp: Optional[str] = Field(default=None, description="Transaction timestamp on blockchain")
    synthetic_entity_id: Optional[str] = Field(default=None, description="Ground truth entity ID (for synthetic evaluation)")
    synthetic_behavior_type: Optional[str] = Field(default=None, description="Ground truth behavior type")
    synthetic_pattern_label: Optional[str] = Field(default=None, description="Ground truth pattern label")

class IngestionMetadata(BaseModel):
    source_file: str
    source_format: str
    ingestion_timestamp: str
    total_records: int
    valid_records: int
    invalid_records: int
    cleaned_records: int
    status: str
