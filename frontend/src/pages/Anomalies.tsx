import React, { useEffect, useState } from 'react';
import { getAnomalies } from '../services/api';
import { AnomalyRecord } from '../types';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const Anomalies: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnom = async () => {
      try {
        const data = await getAnomalies({ limit: 100, only_anomalies: true });
        setAnomalies(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnom();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-warning-600" />
          AI / ML Anomaly Detection Engine
        </h2>
        <p className="text-xs text-content-500 mt-1">
          Unsupervised anomaly scoring using scikit-learn Isolation Forest on scaled behavioral feature vectors.
        </p>
      </div>

      <div className="bg-surface-100 border border-surface-300 rounded-xl shadow-lg flex flex-col">
        <div className="overflow-x-auto overflow-y-auto max-h-[650px] rounded-xl custom-scrollbar">
          <table className="w-full text-left text-xs text-content-600 relative">
            <thead className="sticky top-0 z-10 bg-surface-50/95 backdrop-blur font-mono text-[10px] text-content-500 uppercase border-b border-surface-300 shadow-sm">
              <tr>
                <th className="py-3 px-4 font-semibold tracking-wider">Entity ID</th>
                <th className="py-3 px-4 text-right font-semibold tracking-wider">Anomaly Score</th>
                <th className="py-3 px-4 text-center font-semibold tracking-wider">Is Anomaly</th>
                <th className="py-3 px-4 text-right font-semibold tracking-wider">Cluster ID</th>
                <th className="py-3 px-4 font-semibold tracking-wider">Model Engine</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-200/50 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-content-400">
                    <div className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></span>
                      Evaluating anomaly scores...
                    </div>
                  </td>
                </tr>
              ) : anomalies.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-content-400">
                    No anomalies detected.
                  </td>
                </tr>
              ) : (
                anomalies.map((a) => (
                  <tr key={a.entity_id} className="hover:bg-surface-50 transition-colors group">
                    <td className="py-2.5 px-4 text-brand-600 dark:text-brand-400 font-semibold truncate max-w-[200px] group-hover:text-brand-500 transition-colors">{a.entity_id}</td>
                    <td className="py-2.5 px-4 text-right font-bold text-warning-600">
                      {(a.normalized_anomaly_score ?? a.anomaly_score).toFixed(4)}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <span className="inline-flex items-center justify-center px-2 py-0.5 rounded text-[9px] font-bold tracking-widest bg-critical-500/10 text-critical-600 border border-critical-500/30 shadow-[0_0_8px_rgba(220,38,38,0.15)]">
                        ANOMALOUS
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right font-semibold text-brand-900 dark:text-brand-100">
                      {a.cluster_id === -1 ? 'Outlier (Noise)' : a.cluster_id}
                    </td>
                    <td className="py-2.5 px-4 text-content-500">{a.model_type || 'IsolationForest'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
