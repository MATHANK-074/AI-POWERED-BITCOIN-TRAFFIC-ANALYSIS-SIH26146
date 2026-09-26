import React, { useEffect, useState } from 'react';
import { getClusters } from '../services/api';
import { Layers } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const Clusters: React.FC = () => {
  const [clusters, setClusters] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClust = async () => {
      try {
        const data = await getClusters();
        setClusters(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchClust();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
          <Layers className="w-5 h-5 text-purple-400" />
          Entity Behavior Clustering
        </h2>
        <p className="text-xs text-content-500 mt-1">
          K-Means behavioral clustering and PCA 2D feature projection grouping entity patterns.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cluster Distribution Chart */}
        <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl">
          <h3 className="text-sm font-semibold text-brand-900 mb-4">Cluster Size Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={clusters}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="cluster_id" stroke="#475569" fontSize={12} tickFormatter={(val) => val === -1 ? 'Noise' : `C${val}`} label={{ value: 'Cluster ID', position: 'insideBottom', offset: -5, fill: '#475569' }} />
                <YAxis stroke="#475569" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#0f172a' }} labelFormatter={(label) => label === -1 ? 'Noise / Outliers' : `Cluster ${label}`} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cluster Details Table */}
        <div className="bg-surface-100 border border-surface-300 rounded-xl overflow-hidden shadow-lg p-5">
          <h3 className="text-sm font-semibold text-brand-900 mb-4">Cluster Characteristics</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-content-600 font-mono">
              <thead className="bg-surface-50 text-content-500 text-[11px] uppercase border-b border-surface-300">
                <tr>
                  <th className="p-3">Cluster ID</th>
                  <th className="p-3 text-right">Entity Count</th>
                  <th className="p-3 text-right">Avg Anomaly Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-300">
                {loading ? (
                  <tr>
                    <td colSpan={3} className="p-4 text-center text-content-400">
                      Loading clusters...
                    </td>
                  </tr>
                ) : (
                  clusters.map((c) => (
                    <tr key={c.cluster_id}>
                      <td className="p-3 font-semibold text-purple-400">
                        {c.cluster_id === -1 ? 'Outliers (Noise)' : `Cluster ${c.cluster_id}`}
                      </td>
                      <td className="p-3 text-right font-bold text-brand-900">{c.count}</td>
                      <td className="p-3 text-right text-warning-600 font-semibold">
                        {(c.avg_anomaly ?? 0).toFixed(4)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
