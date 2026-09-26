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

      <div className="bg-surface-100 border border-surface-300 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-content-600">
            <thead className="bg-surface-50 text-content-500 font-mono text-[11px] uppercase border-b border-surface-300">
              <tr>
                <th className="p-3">Entity ID</th>
                <th className="p-3 text-right">Anomaly Score</th>
                <th className="p-3 text-center">Is Anomaly</th>
                <th className="p-3 text-right">Cluster ID</th>
                <th className="p-3">Model Engine</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-300 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-content-400">
                    Evaluating anomaly scores...
                  </td>
                </tr>
              ) : anomalies.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-content-400">
                    No anomalies detected.
                  </td>
                </tr>
              ) : (
                anomalies.map((a) => (
                  <tr key={a.entity_id} className="hover:bg-surface-200 transition-all">
                    <td className="p-3 text-brand-600 dark:text-brand-400 font-semibold truncate max-w-[200px]">{a.entity_id}</td>
                    <td className="p-3 text-right font-bold text-warning-600">
                      {(a.normalized_anomaly_score ?? a.anomaly_score).toFixed(4)}
                    </td>
                    <td className="p-3 text-center">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-critical-50 text-critical-600 border border-critical-500">
                        ANOMALOUS
                      </span>
                    </td>
                    <td className="p-3 text-right font-semibold text-brand-900 dark:text-brand-100">
                      {a.cluster_id === -1 ? 'Outlier (Noise)' : a.cluster_id}
                    </td>
                    <td className="p-3 text-content-500">{a.model_type || 'IsolationForest'}</td>
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
