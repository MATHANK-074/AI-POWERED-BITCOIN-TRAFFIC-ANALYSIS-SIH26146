import React, { useEffect, useState } from 'react';
import { getEvidence } from '../services/api';
import { EvidenceAuditRecord } from '../types';
import { X, ShieldAlert, FileCode, CheckCircle, Cpu, Database, HelpCircle } from 'lucide-react';

interface EvidencePanelProps {
  entityId: string;
  onClose: () => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ entityId, onClose }) => {
  const [evidenceRecords, setEvidenceRecords] = useState<EvidenceAuditRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEv = async () => {
      try {
        const data = await getEvidence(entityId);
        setEvidenceRecords(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEv();
  }, [entityId]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-surface-50 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-surface-100 border-l border-surface-300 h-full overflow-y-auto p-6 shadow-2xl flex flex-col justify-between">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-surface-300 pb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-6 h-6 text-critical-600" />
              <div>
                <h3 className="text-base font-bold text-brand-900 dark:text-brand-100">Evidence & Audit Traceability</h3>
                <p className="text-xs text-content-500 font-mono">Entity Target: {entityId}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-content-500 hover:text-brand-900 dark:text-brand-100 bg-surface-200 rounded-lg transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-content-400">Retrieving evidence audit trail...</div>
          ) : evidenceRecords.length === 0 ? (
            <div className="py-12 text-center text-xs text-content-400">No evidence records found for target entity.</div>
          ) : (
            evidenceRecords.map((ev) => {
              let features: any = {};
              let correlation: any = {};
              try {
                features = typeof ev.feature_snapshot === 'string' ? JSON.parse(ev.feature_snapshot) : ev.feature_snapshot || {};
                correlation = typeof ev.correlation_evidence === 'string' ? JSON.parse(ev.correlation_evidence) : ev.correlation_evidence || {};
              } catch (e) {}

              return (
                <div key={ev.evidence_id} className="space-y-4">
                  {/* Q1: Why did system flag this? */}
                  <div className="p-4 bg-surface-50 border border-surface-300 rounded-xl space-y-3">
                    <h4 className="text-xs font-bold text-warning-600 uppercase flex items-center gap-1.5 font-mono">
                      <HelpCircle className="w-4 h-4 text-warning-600" />
                      1. Why did the system flag this entity?
                    </h4>
                    <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                      <div className="p-2.5 bg-surface-100 rounded border border-surface-300">
                        <span className="text-content-500 block text-[10px]">Priority Score</span>
                        <span className="text-critical-600 font-bold text-base">{features.priority_score ?? 'N/A'}/100</span>
                      </div>
                      <div className="p-2.5 bg-surface-100 rounded border border-surface-300">
                        <span className="text-content-500 block text-[10px]">Anomaly Score</span>
                        <span className="text-brand-600 dark:text-brand-400 font-bold text-base">{features.anomaly_score ?? 'N/A'}</span>
                      </div>
                      <div className="p-2.5 bg-surface-100 rounded border border-surface-300">
                        <span className="text-content-500 block text-[10px]">Correlation Confidence</span>
                        <span className="text-verified-600 font-bold text-base">{features.confidence_score ?? 'N/A'}</span>
                      </div>
                      <div className="p-2.5 bg-surface-100 rounded border border-surface-300">
                        <span className="text-content-500 block text-[10px]">Assigned Cluster ID</span>
                        <span className="text-purple-400 font-bold text-base">
                          {features.cluster_id === -1 ? 'Outlier (Noise)' : `Cluster #${features.cluster_id ?? 'N/A'}`}
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-surface-100 rounded border border-surface-300 text-[11px] font-mono text-content-600">
                      <span className="text-content-500 block mb-1">Scoring Formula:</span>
                      <code>{ev.priority_formula}</code>
                    </div>
                  </div>

                  {/* Q2: Where did this evidence come from? */}
                  <div className="p-4 bg-surface-50 border border-surface-300 rounded-xl space-y-3">
                    <h4 className="text-xs font-bold text-brand-600 dark:text-brand-400 uppercase flex items-center gap-1.5 font-mono">
                      <Database className="w-4 h-4 text-brand-600 dark:text-brand-400" />
                      2. Where did this evidence come from?
                    </h4>
                    <div className="space-y-2 text-xs font-mono">
                      <div className="flex justify-between py-1 border-b border-surface-300">
                        <span className="text-content-500">Source File:</span>
                        <span className="text-brand-900 dark:text-brand-100 font-semibold">{ev.source_file}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-surface-300">
                        <span className="text-content-500">Record Row Index:</span>
                        <span className="text-brand-900 dark:text-brand-100">#{ev.source_record_index}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-surface-300">
                        <span className="text-content-500">Pipeline Ingestion Stage:</span>
                        <span className="text-brand-900 dark:text-brand-100">{ev.pipeline_stage}</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-surface-300">
                        <span className="text-content-500">ML Model Engine:</span>
                        <span className="text-verified-600">{ev.model_version}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-content-500">Timestamp UTC:</span>
                        <span className="text-content-600">{ev.created_at}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="pt-4 border-t border-surface-300 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-surface-200 hover:bg-surface-300 text-brand-900 dark:text-brand-100 text-xs font-semibold rounded-lg transition-all"
          >
            Close Audit Trail
          </button>
        </div>
      </div>
    </div>
  );
};
