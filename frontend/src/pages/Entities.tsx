import React, { useEffect, useState } from 'react';
import { getEntities, getEntityProfile } from '../services/api';
import { EntityProfile } from '../types';
import { Users, Search, UserCheck, Activity } from 'lucide-react';

export const Entities: React.FC = () => {
  const [entities, setEntities] = useState<EntityProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
  const [search, setSearch] = useState('');

  const fetchEntities = async () => {
    setLoading(true);
    try {
      const data = await getEntities({ limit: 100, search: search || undefined });
      setEntities(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, []);

  const handleInspect = async (id: string) => {
    try {
      const prof = await getEntityProfile(id);
      setSelectedEntity(prof);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-brand-900 flex items-center gap-2">
          <Users className="w-5 h-5 text-verified-600" />
          Entity Profile Explorer
        </h2>
        <p className="text-xs text-content-500 mt-1">
          Inspect behavioral features, fan-in/fan-out topology, burst scores, and transaction history for wallet and IP entities.
        </p>
      </div>

      {/* Filter */}
      <div className="bg-surface-100 border border-surface-300 p-4 rounded-xl flex items-center gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-content-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search entity ID (Wallet Address or IP)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-surface-50 border border-surface-300 rounded-lg pl-9 pr-3 py-1.5 text-xs text-brand-900 placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
        <button
          onClick={fetchEntities}
          className="px-4 py-1.5 bg-verified-600 hover:bg-verified-500 text-brand-900 text-xs font-medium rounded-lg transition-all"
        >
          Search
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Entities Table */}
        <div className="lg:col-span-2 bg-surface-100 border border-surface-300 rounded-xl overflow-hidden shadow-lg">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-content-600">
              <thead className="bg-surface-50 text-content-500 font-mono text-[11px] uppercase border-b border-surface-300">
                <tr>
                  <th className="p-3">Entity ID</th>
                  <th className="p-3">Type</th>
                  <th className="p-3 text-right">TX Count</th>
                  <th className="p-3 text-right">Total Volume (BTC)</th>
                  <th className="p-3 text-right">In/Out Ratio</th>
                  <th className="p-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-300 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-content-400">
                      Loading entity profiles...
                    </td>
                  </tr>
                ) : (
                  entities.map((e) => (
                    <tr key={e.entity_id} className="hover:bg-surface-200 transition-all">
                      <td className="p-3 text-brand-600 font-semibold truncate max-w-[150px]" title={e.entity_id}>
                        {e.entity_id}
                      </td>
                      <td className="p-3 uppercase text-[10px]">
                        <span
                          className={`px-2 py-0.5 rounded font-bold ${
                            e.entity_type === 'wallet'
                              ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                              : 'bg-brand-500/20 text-brand-600 border border-brand-500/30'
                          }`}
                        >
                          {e.entity_type}
                        </span>
                      </td>
                      <td className="p-3 text-right font-semibold text-brand-900">{e.tx_count}</td>
                      <td className="p-3 text-right font-semibold text-verified-600">
                        {e.total_amount_btc.toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-content-500">{e.in_out_ratio}</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => handleInspect(e.entity_id)}
                          className="px-2.5 py-1 bg-surface-200 hover:bg-surface-300 text-brand-900 text-[11px] rounded transition-all"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Entity Inspector Panel */}
        <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl">
          <h3 className="text-sm font-semibold text-brand-900 mb-4 flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-brand-600" /> Entity Detail Inspector
          </h3>

          {!selectedEntity ? (
            <p className="text-xs text-content-400 py-10 text-center">
              Click 'Inspect' on any entity row to view detailed features.
            </p>
          ) : (
            <div className="space-y-4 text-xs font-mono">
              <div className="p-3 bg-surface-50 rounded-lg">
                <span className="text-[11px] text-content-400 block">Entity ID</span>
                <span className="text-xs font-bold text-brand-600 break-all">{selectedEntity.entity_profile.entity_id}</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Avg Amount</span>
                  <span className="text-xs font-bold text-brand-900">{selectedEntity.entity_profile.avg_amount_btc} BTC</span>
                </div>
                <div className="p-2.5 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Max Amount</span>
                  <span className="text-xs font-bold text-verified-600">{selectedEntity.entity_profile.max_amount_btc} BTC</span>
                </div>
                <div className="p-2.5 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">In Degree</span>
                  <span className="text-xs font-bold text-brand-900">{selectedEntity.entity_profile.in_degree}</span>
                </div>
                <div className="p-2.5 bg-surface-50 rounded-lg">
                  <span className="text-[10px] text-content-400 block">Out Degree</span>
                  <span className="text-xs font-bold text-brand-900">{selectedEntity.entity_profile.out_degree}</span>
                </div>
              </div>

              {selectedEntity.anomaly_info?.anomaly_score != null && (
                <div className="p-3 bg-warning-500/10 border border-warning-500 rounded-lg">
                  <span className="text-[11px] text-warning-600 block font-semibold">Anomaly Assessment</span>
                  <p className="text-xs text-content-600 mt-1">
                    Normalized Anomaly Score: <span className="font-bold text-warning-600">{selectedEntity.anomaly_info.normalized_anomaly_score}</span>
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
