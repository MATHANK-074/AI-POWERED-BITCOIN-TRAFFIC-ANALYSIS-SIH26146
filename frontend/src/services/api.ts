import axios from 'axios';
import { SystemStats, Transaction, EntityProfile, AnomalyRecord, InvestigationLead, CytoscapeGraphData } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getIngestStatus = async () => {
  const res = await api.get('/ingest/status');
  return res.data;
};

export const getMapMarkers = async () => {
  const res = await api.get('/ingest/map-markers');
  return res.data;
};

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/ingest', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const getTransactions = async (params: Record<string, any> = {}) => {
  const res = await api.get<Transaction[]>('/transactions', { params });
  return res.data;
};

export const getTransactionByTxid = async (txid: string) => {
  const res = await api.get<Transaction>(`/transactions/${txid}`);
  return res.data;
};

export const getEntities = async (params: Record<string, any> = {}) => {
  const res = await api.get<EntityProfile[]>('/entities', { params });
  return res.data;
};

export const getEntityProfile = async (id: string) => {
  const res = await api.get(`/entities/${id}`);
  return res.data;
};

export const getGraph = async (nodeId?: string, maxDepth: number = 2) => {
  const url = nodeId ? `/graph/${nodeId}` : '/graph';
  const res = await api.get<{ graph: CytoscapeGraphData; statistics: any; top_high_degree_entities: any[] }>(url, {
    params: { max_depth: maxDepth },
  });
  return res.data;
};

export const getAnomalies = async (params: Record<string, any> = {}) => {
  const res = await api.get<AnomalyRecord[]>('/anomalies', { params });
  return res.data;
};

export const getClusters = async () => {
  const res = await api.get<any[]>('/anomalies/clusters');
  return res.data;
};

export const getLeads = async (params: Record<string, any> = {}) => {
  const res = await api.get<InvestigationLead[]>('/leads', { params });
  return res.data;
};

export const getLeadById = async (id: string) => {
  const res = await api.get<InvestigationLead>(`/leads/${id}`);
  return res.data;
};

export const getModelEvaluation = async () => {
  const res = await api.get('/evaluation');
  return res.data;
};

export const getCases = async () => {
  const res = await api.get<any[]>('/cases');
  return res.data;
};

export const createCase = async (payload: any) => {
  const res = await api.post('/cases', payload);
  return res.data;
};

export const updateCase = async (caseId: string, payload: any) => {
  const res = await api.put(`/cases/${caseId}`, payload);
  return res.data;
};

export const deleteCase = async (caseId: string) => {
  const res = await api.delete(`/cases/${caseId}`);
  return res.data;
};

export const exportCaseReport = async (caseId: string) => {
  const res = await api.get(`/cases/${caseId}/export`);
  return res.data;
};

export const getEvidence = async (entityId: string) => {
  const res = await api.get<any[]>(`/evidence/${entityId}`);
  return res.data;
};

export const searchGraphPath = async (source: string, target: string) => {
  const res = await api.get('/graph/path/search', { params: { source, target } });
  return res.data;
};

export default api;
