import React, { useEffect, useState } from 'react';
import { getCases, createCase, updateCase, deleteCase, exportCaseReport } from '../services/api';
import { InvestigationCase } from '../types';
import { FolderKanban, Plus, FileText, Trash2, Edit3, Download, CheckCircle2, Clock, AlertTriangle, ShieldCheck, X } from 'lucide-react';

export const Cases: React.FC = () => {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<InvestigationCase | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'OPEN' | 'UNDER INVESTIGATION' | 'RESOLVED' | 'ARCHIVED'>('OPEN');
  const [assignedTo, setAssignedTo] = useState('Lead Investigator');
  const [entitiesInput, setEntitiesInput] = useState('');
  const [notes, setNotes] = useState('');

  const fetchCases = async () => {
    try {
      const data = await getCases();
      setCases(data);
      if (data.length > 0 && !selectedCase) {
        setSelectedCase(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const entitiesList = entitiesInput.split(',').map((s) => s.trim()).filter(Boolean);
      await createCase({
        title,
        description,
        status,
        assigned_to: assignedTo,
        entities: entitiesList,
        notes,
      });
      setIsCreateOpen(false);
      setTitle('');
      setDescription('');
      setEntitiesInput('');
      setNotes('');
      fetchCases();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteCase = async (caseId: string) => {
    if (confirm(`Delete case ${caseId}?`)) {
      try {
        await deleteCase(caseId);
        if (selectedCase?.case_id === caseId) setSelectedCase(null);
        fetchCases();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleExport = async (caseId: string) => {
    try {
      const report = await exportCaseReport(caseId);
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `Case_Report_${caseId}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
            <FolderKanban className="w-5 h-5 text-brand-600 dark:text-brand-400" />
            Investigation Case Management
          </h2>
          <p className="text-xs text-content-500 mt-1">
            Organize suspicious transactions, wallet profiles, and priority leads into formal investigative cases.
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="px-3.5 py-2 bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 shadow-lg"
        >
          <Plus className="w-4 h-4" /> Create New Case
        </button>
      </div>

      {/* Case Management Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cases List Table */}
        <div className="lg:col-span-2 bg-surface-100 border border-surface-300 rounded-xl shadow-lg flex flex-col">
          <div className="overflow-x-auto overflow-y-auto max-h-[650px] rounded-xl custom-scrollbar">
            <table className="w-full text-left text-xs text-content-600 relative">
              <thead className="sticky top-0 z-10 bg-surface-50/95 backdrop-blur font-mono text-[10px] text-content-500 uppercase border-b border-surface-300 shadow-sm">
                <tr>
                  <th className="py-3 px-4 font-semibold tracking-wider">Case ID</th>
                  <th className="py-3 px-4 font-semibold tracking-wider">Title</th>
                  <th className="py-3 px-4 text-center font-semibold tracking-wider">Status</th>
                  <th className="py-3 px-4 font-semibold tracking-wider">Assigned To</th>
                  <th className="py-3 px-4 text-right font-semibold tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-200/50 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-content-400">
                      <div className="flex items-center justify-center gap-2">
                        <span className="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></span>
                        Loading investigation cases...
                      </div>
                    </td>
                  </tr>
                ) : cases.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-content-400">
                      No investigation cases created yet. Click "Create New Case" above.
                    </td>
                  </tr>
                ) : (
                  cases.map((c) => (
                    <tr
                      key={c.case_id}
                      onClick={() => setSelectedCase(c)}
                      className={`cursor-pointer transition-colors group ${
                        selectedCase?.case_id === c.case_id ? 'bg-brand-500/10' : 'hover:bg-surface-50'
                      }`}
                    >
                      <td className="py-2.5 px-4 font-semibold text-brand-900 dark:text-brand-100 group-hover:text-brand-600 transition-colors">{c.case_id}</td>
                      <td className="py-2.5 px-4 font-medium text-content-700">{c.title}</td>
                      <td className="py-2.5 px-4 text-center">
                        <span
                          className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded text-[9px] font-bold tracking-widest ${
                            c.status === 'OPEN'
                              ? 'bg-warning-500/10 text-warning-600 border border-warning-500/30'
                              : c.status === 'UNDER INVESTIGATION'
                              ? 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/30'
                              : c.status === 'RESOLVED'
                              ? 'bg-verified-500/10 text-verified-600 border border-verified-500/30'
                              : 'bg-surface-200 text-content-500 border-surface-300'
                          }`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-content-600">{c.assigned_to || 'Unassigned'}</td>
                      <td className="py-2.5 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteCase(c.case_id);
                          }}
                          className="p-1 text-content-500 hover:text-critical-600 transition-all rounded hover:bg-surface-200"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Case Inspector */}
        <div className="bg-surface-100 border border-surface-300 rounded-xl p-5 space-y-4 shadow-lg">
          {selectedCase ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="flex justify-between items-center border-b border-surface-300 pb-3">
                <span className="font-bold text-sm text-brand-600 dark:text-brand-400">{selectedCase.case_id}</span>
                <button
                  onClick={() => handleExport(selectedCase.case_id)}
                  className="px-2.5 py-1 bg-surface-200 hover:bg-surface-300 text-brand-900 dark:text-brand-100 text-[11px] rounded border border-surface-400 flex items-center gap-1 transition-all"
                >
                  <Download className="w-3 h-3" /> Export Report
                </button>
              </div>

              <div>
                <span className="text-content-500 text-[10px] uppercase block mb-1">Case Title</span>
                <span className="text-content-700 font-semibold text-sm">{selectedCase.title}</span>
              </div>

              <div>
                <span className="text-content-500 text-[10px] uppercase block mb-1">Description</span>
                <p className="text-content-600 bg-surface-50 p-2.5 rounded border border-surface-300 font-sans text-xs">
                  {selectedCase.description || 'No description provided.'}
                </p>
              </div>

              <div>
                <span className="text-content-500 text-[10px] uppercase block mb-1">Target Entities / Wallets</span>
                <div className="p-2.5 bg-surface-50 rounded border border-surface-300 space-y-1 text-brand-600 dark:text-brand-400">
                  {typeof selectedCase.entities === 'string'
                    ? selectedCase.entities
                    : selectedCase.entities.length > 0
                    ? selectedCase.entities.join(', ')
                    : 'None attached.'}
                </div>
              </div>

              <div>
                <span className="text-content-500 text-[10px] uppercase block mb-1">Investigator Analysis Notes</span>
                <p className="text-content-600 bg-surface-50 p-2.5 rounded border border-surface-300 font-sans text-xs">
                  {selectedCase.notes || 'No notes added.'}
                </p>
              </div>

              <div className="text-[10px] text-content-400 pt-2 border-t border-surface-300 flex justify-between">
                <span>Created: {selectedCase.created_at}</span>
                <span>Updated: {selectedCase.updated_at}</span>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-content-400">
              Select a case from the table to view details.
            </div>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-surface-50 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-surface-100 border border-surface-300 rounded-xl p-6 shadow-2xl space-y-5">
            <div className="flex justify-between items-center border-b border-surface-300 pb-3">
              <h3 className="text-sm font-bold text-brand-900 dark:text-brand-100 flex items-center gap-2">
                <FolderKanban className="w-4 h-4 text-brand-600 dark:text-brand-400" /> Create Investigation Case
              </h3>
              <button onClick={() => setIsCreateOpen(false)} className="text-content-500 hover:text-brand-900 dark:text-brand-100">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateCase} className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-content-500 mb-1">Case Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Operation Darknet Wallet Cluster Analysis"
                  className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-content-500 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief summary of investigative scope..."
                  className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500 font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-content-500 mb-1">Status</label>
                  <select
                    value={status}
                    onChange={(e: any) => setStatus(e.target.value)}
                    className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500"
                  >
                    <option value="OPEN">OPEN</option>
                    <option value="UNDER INVESTIGATION">UNDER INVESTIGATION</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="ARCHIVED">ARCHIVED</option>
                  </select>
                </div>
                <div>
                  <label className="block text-content-500 mb-1">Assigned Investigator</label>
                  <input
                    type="text"
                    value={assignedTo}
                    onChange={(e) => setAssignedTo(e.target.value)}
                    className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-content-500 mb-1">Target Entity IDs (comma-separated)</label>
                <input
                  type="text"
                  value={entitiesInput}
                  onChange={(e) => setEntitiesInput(e.target.value)}
                  placeholder="e.g. 192.168.1.50, bc1qtest1..."
                  className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block text-content-500 mb-1">Initial Notes</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Additional case background notes..."
                  className="w-full bg-surface-50 border border-surface-300 rounded p-2.5 text-brand-900 dark:text-brand-100 focus:outline-none focus:border-brand-500 font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-4 py-2 bg-surface-200 text-content-600 rounded hover:bg-surface-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-brand-600 text-white rounded hover:bg-brand-500 font-semibold"
                >
                  Save Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
