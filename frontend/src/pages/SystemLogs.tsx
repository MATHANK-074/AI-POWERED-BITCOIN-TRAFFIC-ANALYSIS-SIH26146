import React, { useEffect, useState } from 'react';
import { getHealth, getIngestStatus } from '../services/api';
import { Terminal, CheckCircle, Server } from 'lucide-react';

export const SystemLogs: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const h = await getHealth();
        setHealth(h);
        const s = await getIngestStatus();
        setStatus(s);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInfo();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
          <Terminal className="w-5 h-5 text-brand-600" />
          System & Ingestion Logs
        </h2>
        <p className="text-xs text-content-500 mt-1">
          System status, offline runtime configuration, database integrity, and background job logs.
        </p>
      </div>

      <div className="bg-surface-100 border border-surface-300 p-6 rounded-xl space-y-4">
        <h3 className="text-sm font-semibold text-brand-900 flex items-center gap-2">
          <Server className="w-4 h-4 text-verified-600" /> Backend Environment & Runtime State
        </h3>

        {loading ? (
          <p className="text-xs text-content-400">Loading system status...</p>
        ) : (
          <div className="bg-surface-50 p-4 rounded-xl font-mono text-xs text-content-600 space-y-2 border border-surface-300">
            <div className="flex justify-between border-b border-surface-300 pb-2">
              <span className="text-content-400">System Name:</span>
              <span className="text-brand-600 font-bold">{health?.system}</span>
            </div>
            <div className="flex justify-between border-b border-surface-300 pb-2">
              <span className="text-content-400">Version:</span>
              <span className="text-brand-900">{health?.version}</span>
            </div>
            <div className="flex justify-between border-b border-surface-300 pb-2">
              <span className="text-content-400">Offline Mode:</span>
              <span className="text-verified-600 font-bold">{String(health?.offline_mode)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-content-400">Pipeline Execution Running:</span>
              <span className="text-warning-600 font-bold">{String(status?.pipeline_running)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
