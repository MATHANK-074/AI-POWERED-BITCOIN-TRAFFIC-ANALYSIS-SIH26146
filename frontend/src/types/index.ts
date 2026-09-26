export interface SystemStats {
  total_transactions: number;
  total_wallets: number;
  total_ips: number;
  correlated_events: number;
  anomalies_detected: number;
  investigation_leads: number;
}

export interface Transaction {
  txid: string;
  timestamp: string;
  src_ip?: string;
  dst_ip?: string;
  src_port?: number;
  dst_port?: number;
  input_wallet?: string;
  output_wallet?: string;
  amount_btc: number;
  fee_btc?: number;
  block_height?: number;
  protocol?: string;
  country?: string;
  city?: string;
}

export interface EntityProfile {
  entity_id: string;
  entity_type: 'wallet' | 'ip' | 'txid';
  tx_count: number;
  total_amount_btc: number;
  avg_amount_btc: number;
  max_amount_btc: number;
  min_amount_btc: number;
  avg_fee_btc: number;
  unique_ip_count: number;
  unique_counterparties: number;
  in_degree: number;
  out_degree: number;
  in_out_ratio: number;
  burst_score: number;
}

export interface AnomalyRecord {
  entity_id: string;
  anomaly_score: number;
  normalized_anomaly_score: number;
  is_anomaly: boolean;
  cluster_id: number;
  pca_x?: number;
  pca_y?: number;
  model_type?: string;
}

export interface InvestigationLead {
  lead_id: string;
  entity_id: string;
  txid?: string;
  entity_type: string;
  priority_score: number;
  priority_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  anomaly_score: number;
  confidence_score: number;
  cluster_id: number;
  connected_entities_count: number;
  correlated_events_count: number;
  reasons: string[] | string;
  supporting_evidence: string;
  created_at: string;
}

export interface CytoscapeNodeData {
  id: string;
  label: string;
  type: string;
  anomaly_score?: number;
  is_anomaly?: boolean;
  cluster_id?: number;
  amount_btc?: number;
}

export interface CytoscapeEdgeData {
  id: string;
  source: string;
  target: string;
  relationship: string;
  amount_btc?: number;
}

export interface CytoscapeGraphData {
  nodes: { data: CytoscapeNodeData }[];
  edges: { data: CytoscapeEdgeData }[];
}

export interface InvestigationCase {
  case_id: string;
  title: string;
  description?: string;
  status: 'OPEN' | 'UNDER INVESTIGATION' | 'RESOLVED' | 'ARCHIVED';
  assigned_to?: string;
  entities: string[] | string;
  leads: string[] | string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface EvidenceAuditRecord {
  evidence_id: string;
  entity_id: string;
  entity_type: string;
  source_file: string;
  source_record_index: number;
  ingestion_timestamp: string;
  pipeline_stage: string;
  feature_snapshot: string;
  correlation_evidence: string;
  model_version: string;
  priority_formula: string;
  created_at: string;
}

export interface GraphPathResponse {
  source: string;
  target: string;
  path_found: boolean;
  path_length?: number;
  path_nodes?: string[];
  graph: CytoscapeGraphData;
}
