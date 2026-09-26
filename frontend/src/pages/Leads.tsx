import React, { useEffect, useState } from 'react';
import { getLeads } from '../services/api';
import { InvestigationLead } from '../types';
import { FileText, Download, AlertOctagon, Info } from 'lucide-react';

export const Leads: React.FC = () => {
  const [leads, setLeads] = useState<InvestigationLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<InvestigationLead | null>(null);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const data = await getLeads({ limit: 100 });
        setLeads(data);
        if (data.length > 0) {
          setSelectedLead(data[0]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLeads();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-critical-600" />
            Explainable Priority Investigative Leads
          </h2>
          <p className="text-xs text-content-500 mt-1">
            Prioritized leads generated from transparent multi-factor scoring (Anomaly + Correlation + Pattern + Graph).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="http://127.0.0.1:8000/api/export/leads/csv"
            target="_blank"
            rel="noreferrer"
            className="px-3.5 py-2 bg-surface-200 hover:bg-surface-300 text-brand-900 dark:text-brand-100 text-xs font-medium rounded-lg border border-surface-400 transition-all flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" /> Leads CSV
          </a>
          <a
            href="http://127.0.0.1:8000/api/export/report/html"
            target="_blank"
            rel="noreferrer"
            className="px-3.5 py-2 bg-critical-600 hover:bg-critical-500 text-white text-xs font-medium rounded-lg transition-all flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" /> HTML Report
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leads Table */}
        <div className="lg:col-span-2 bg-surface-100 border border-surface-300 rounded-xl shadow-lg flex flex-col">
          <div className="overflow-x-auto overflow-y-auto max-h-[650px] rounded-xl custom-scrollbar">
            <table className="w-full text-left text-xs text-content-600 relative">
              <thead className="sticky top-0 z-10 bg-surface-50/95 backdrop-blur font-mono text-[10px] text-content-500 uppercase border-b border-surface-300 shadow-sm">
                <tr>
                  <th className="py-3 px-4 font-semibold tracking-wider">Lead ID</th>
                  <th className="py-3 px-4 font-semibold tracking-wider">Target Entity</th>
                  <th className="py-3 px-4 text-right font-semibold tracking-wider">Priority Score</th>
                  <th className="py-3 px-4 text-center font-semibold tracking-wider">Priority Level</th>
                  <th className="py-3 px-4 text-right font-semibold tracking-wider">Confidence</th>
                  <th className="py-3 px-4 text-center font-semibold tracking-wider">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-200/50 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-content-400">
                      <div className="flex items-center justify-center gap-2">
                        <span className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></span>
                        Generating prioritized investigative leads...
                      </div>
                    </td>
                  </tr>
                ) : (
                  leads.map((lead) => (
                    <tr
                      key={lead.lead_id}
                      onClick={() => setSelectedLead(lead)}
                      className={`cursor-pointer transition-colors group ${
                        selectedLead?.lead_id === lead.lead_id ? 'bg-brand-500/10' : 'hover:bg-surface-50'
                      }`}
                    >
                      <td className="py-2.5 px-4 font-semibold text-brand-900 dark:text-brand-100">{lead.lead_id}</td>
                      <td className="py-2.5 px-4 text-brand-600 dark:text-brand-400 truncate max-w-[140px] group-hover:text-brand-500 transition-colors">{lead.entity_id}</td>
                      <td className="py-2.5 px-4 text-right font-bold text-critical-600">{lead.priority_score}/100</td>
                      <td className="py-2.5 px-4 text-center">
                        <span
                          className={`inline-flex items-center justify-center px-2 py-0.5 rounded text-[9px] font-bold tracking-widest ${
                            lead.priority_level === 'CRITICAL'
                              ? 'bg-critical-500/10 text-critical-600 border border-critical-500/30 shadow-[0_0_8px_rgba(220,38,38,0.15)]'
                              : lead.priority_level === 'HIGH'
                              ? 'bg-warning-500/10 text-warning-600 border border-warning-500/30 shadow-[0_0_8px_rgba(234,179,8,0.15)]'
                              : 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                          }`}
                        >
                          {lead.priority_level}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-right text-verified-600 font-semibold">{lead.confidence_score}</td>
                      <td className="py-2.5 px-4 text-center">
                        <button className="px-2.5 py-1 bg-surface-200 hover:bg-brand-600 hover:text-white text-content-600 text-[10px] rounded transition-colors font-semibold">
                          View
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Explainable Lead Detail Card */}
        <div className="bg-surface-100 border border-surface-300 p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-brand-900 dark:text-brand-100 mb-4 flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-critical-600" /> Explainability & Audit Trail
            </h3>

            {!selectedLead ? (
              <p className="text-xs text-content-400 py-10 text-center">Select a lead to inspect explanation reasons.</p>
            ) : (
              <div className="space-y-4 font-mono text-xs">
                <div className="p-3 bg-surface-50 rounded-lg flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-content-400 block">Lead Identifier</span>
                    <span className="text-xs font-bold text-brand-900 dark:text-brand-100">{selectedLead.lead_id}</span>
                  </div>
                  <span className="text-base font-bold text-critical-600">{selectedLead.priority_score}/100</span>
                </div>

                <div>
                  <h4 className="text-[11px] font-semibold text-content-600 mb-2 uppercase tracking-wide">
                    Why was this lead flagged?
                  </h4>
                  <ul className="space-y-2">
                    {Array.isArray(selectedLead.reasons) ? (
                      selectedLead.reasons.map((r, i) => (
                        <li key={i} className="p-2.5 bg-surface-50 border border-surface-300 rounded text-[11px] text-content-600">
                          {r}
                        </li>
                      ))
                    ) : (
                      <li className="p-2.5 bg-surface-50 border border-surface-300 rounded text-[11px] text-content-600">
                        {selectedLead.reasons}
                      </li>
                    )}
                  </ul>
                </div>

                <div className="p-3 bg-surface-50 rounded-lg border border-surface-300">
                  <span className="text-[10px] text-content-400 block mb-1">Audit Trail Evidence</span>
                  <pre className="text-[10px] text-content-500 whitespace-pre-wrap font-mono">
                    {selectedLead.supporting_evidence}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
