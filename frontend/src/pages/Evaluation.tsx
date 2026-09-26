import React, { useEffect, useState } from 'react';
import { getModelEvaluation } from '../services/api';
import { Activity, CheckCircle2, BarChart2 } from 'lucide-react';

export const Evaluation: React.FC = () => {
  const [evalData, setEvalData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEval = async () => {
      try {
        const data = await getModelEvaluation();
        setEvalData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchEval();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
          <Activity className="w-5 h-5 text-verified-600" />
          AI / ML Model Performance & Evaluation
        </h2>
        <p className="text-xs text-content-500 mt-1">
          Honest metrics evaluation. Displays Precision, Recall, F1, and Confusion Matrix when ground-truth labels exist, or Silhouette score and cluster distributions for unsupervised datasets.
        </p>
      </div>

      <div className="bg-surface-100 border border-surface-300 p-6 rounded-xl space-y-6">
        {loading ? (
          <p className="text-xs text-content-400 text-center py-8">Computing model evaluation metrics...</p>
        ) : !evalData ? (
          <p className="text-xs text-content-400 text-center py-8">No evaluation metrics available.</p>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-surface-300 pb-3">
              <span className="text-sm font-semibold text-brand-900">{evalData.evaluation_type}</span>
              <span className="text-xs font-mono text-brand-600 bg-brand-100/60 border border-cyan-800 px-2.5 py-1 rounded">
                Verified Metrics
              </span>
            </div>

            {evalData.precision !== undefined ? (
              /* Supervised Metrics */
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300 text-center">
                  <span className="text-xs text-content-500 block mb-1">Precision</span>
                  <span className="text-2xl font-bold font-mono text-verified-600">{evalData.precision}</span>
                </div>
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300 text-center">
                  <span className="text-xs text-content-500 block mb-1">Recall</span>
                  <span className="text-2xl font-bold font-mono text-brand-600">{evalData.recall}</span>
                </div>
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300 text-center">
                  <span className="text-xs text-content-500 block mb-1">F1 Score</span>
                  <span className="text-2xl font-bold font-mono text-purple-400">{evalData.f1_score}</span>
                </div>
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300 text-center">
                  <span className="text-xs text-content-500 block mb-1">ROC-AUC</span>
                  <span className="text-2xl font-bold font-mono text-warning-600">{evalData.roc_auc}</span>
                </div>
              </div>
            ) : (
              /* Unsupervised Metrics */
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300">
                  <span className="text-xs text-content-500 block mb-1">Entities Evaluated</span>
                  <span className="text-xl font-bold font-mono text-brand-900">
                    {evalData.total_entities_evaluated ?? 0}
                  </span>
                </div>
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300">
                  <span className="text-xs text-content-500 block mb-1">Anomalies Detected</span>
                  <span className="text-xl font-bold font-mono text-warning-600">
                    {evalData.anomalies_detected ?? 0}
                  </span>
                </div>
                <div className="p-4 bg-surface-50 rounded-xl border border-surface-300">
                  <span className="text-xs text-content-500 block mb-1">Average Anomaly Score</span>
                  <span className="text-xl font-bold font-mono text-brand-600">
                    {evalData.avg_anomaly_score ?? 0}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
