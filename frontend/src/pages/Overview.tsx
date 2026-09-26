import React, { useEffect, useState } from 'react';
import { getIngestStatus, getLeads, getMapMarkers } from '../services/api';
import { SystemStats, InvestigationLead } from '../types';
import { ShieldAlert, ListFilter, Users, Network, AlertTriangle, FileText, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { MapChart } from '../components/MapChart';

interface OverviewProps {
  onNavigate: (tab: string) => void;
}

export const Overview: React.FC<OverviewProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [topLeads, setTopLeads] = useState<InvestigationLead[]>([]);
  const [markers, setMarkers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statusRes = await getIngestStatus();
        setStats(statusRes.database_stats || null);
        const leadsRes = await getLeads({ limit: 5 });
        setTopLeads(leadsRes);
        const mapRes = await getMapMarkers();
        if (mapRes && mapRes.markers) {
          setMarkers(mapRes.markers);
        }
      } catch (err) {
        console.error('Error fetching overview data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const chartData = [
    { name: 'Transactions', count: stats?.total_transactions || 0 },
    { name: 'Wallets', count: stats?.total_wallets || 0 },
    { name: 'Network IPs', count: stats?.total_ips || 0 },
    { name: 'Correlated', count: stats?.correlated_events || 0 },
    { name: 'Anomalies', count: stats?.anomalies_detected || 0 },
    { name: 'Leads', count: stats?.investigation_leads || 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-surface-100 border border-surface-300 p-6 rounded-xl shadow-lg">
        <div>
          <h2 className="text-2xl font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
            Investigator Command Center
            <span className="text-xs font-mono font-medium px-2.5 py-1 rounded-full bg-verified-50 text-verified-600 border border-verified-500">
              OFFLINE READY
            </span>
          </h2>
          <p className="text-sm text-content-500 mt-1">
            Bulk cryptocurrency data ingestion, network-blockchain correlation, AI anomaly detection, and explainable leads.
          </p>
        </div>
        <button
          onClick={() => onNavigate('ingestion')}
          className="px-4 py-2.5 bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-400 hover:to-brand-500 text-white font-semibold rounded-lg text-xs shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
        >
          <ShieldAlert className="w-4 h-4" />
          Ingest Dataset
        </button>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {[
          { label: 'Total Transactions', val: stats?.total_transactions, icon: ListFilter, color: 'text-blue-400' },
          { label: 'Unique Wallets', val: stats?.total_wallets, icon: Users, color: 'text-verified-600' },
          { label: 'Network IPs', val: stats?.total_ips, icon: Network, color: 'text-brand-600 dark:text-brand-400' },
          { label: 'Correlated Events', val: stats?.correlated_events, icon: Network, color: 'text-purple-400' },
          { label: 'Detected Anomalies', val: stats?.anomalies_detected, icon: AlertTriangle, color: 'text-warning-600' },
          { label: 'Priority Leads', val: stats?.investigation_leads, icon: FileText, color: 'text-critical-600' },
        ].map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="bg-surface-100 border border-surface-300 p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="text-xs text-content-500 font-medium">{card.label}</span>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <div className="mt-3">
                <span className="text-xl font-bold font-mono text-brand-900 dark:text-brand-100">
                  {loading ? '...' : (card.val ?? 0).toLocaleString()}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid: Chart + Top Leads */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Breakdown Chart */}
        <div className="lg:col-span-2 bg-surface-100 border border-surface-300 p-5 rounded-xl">
          <h3 className="text-sm font-semibold text-brand-900 dark:text-brand-100 mb-4 flex items-center gap-2">
            Dataset Summary Breakdown
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--surface-300)" />
                <XAxis dataKey="name" stroke="var(--content-400)" fontSize={12} />
                <YAxis stroke="var(--content-400)" fontSize={12} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--surface-50)', borderColor: 'var(--surface-300)', color: 'var(--content-700)' }}
                  itemStyle={{ color: '#0369a1' }}
                />
                <Bar dataKey="count" fill="#0369a1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Priority Leads Quick Access */}
        <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-brand-900 dark:text-brand-100 flex items-center gap-2">
                Top Priority Leads
              </h3>
              <button
                onClick={() => onNavigate('leads')}
                className="text-xs text-brand-600 dark:text-brand-400 hover:text-brand-500 flex items-center gap-1 font-medium"
              >
                View All <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
            {topLeads.length === 0 ? (
              <p className="text-xs text-content-400 py-6 text-center">No high-priority leads detected yet.</p>
            ) : (
              <div className="space-y-3">
                {topLeads.map((lead) => (
                  <div
                    key={lead.lead_id}
                    onClick={() => onNavigate('leads')}
                    className="p-3 bg-surface-50 border border-surface-300 rounded-lg cursor-pointer hover:border-surface-400 transition-all flex items-center justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-semibold text-brand-900 dark:text-brand-100">{lead.lead_id}</span>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                            lead.priority_level === 'CRITICAL'
                              ? 'bg-critical-50 text-critical-600 border border-critical-500'
                              : 'bg-warning-50 text-warning-600 border border-warning-500'
                          }`}
                        >
                          {lead.priority_level}
                        </span>
                      </div>
                      <p className="text-[11px] text-content-500 font-mono mt-1 truncate max-w-[200px]">
                        {lead.entity_id}
                      </p>
                    </div>
                    <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400">{lead.priority_score}/100</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Map Section */}
      <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl">
        <h3 className="text-sm font-semibold text-brand-900 dark:text-brand-100 mb-4 flex items-center gap-2">
          Global IP Geographic Distribution
        </h3>
        <div className="w-full h-96">
          <MapChart markers={markers} />
        </div>
      </div>
    </div>
  );
};
