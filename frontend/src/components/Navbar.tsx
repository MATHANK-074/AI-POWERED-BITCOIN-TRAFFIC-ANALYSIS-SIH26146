import React from 'react';
import { 
  ShieldAlert, 
  UploadCloud, 
  ListFilter, 
  Users, 
  Network, 
  AlertTriangle, 
  Layers, 
  FileText, 
  FolderKanban,
  Activity, 
  Terminal 
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: ShieldAlert },
    { id: 'ingestion', label: 'Data Ingestion', icon: UploadCloud },
    { id: 'transactions', label: 'Transactions', icon: ListFilter },
    { id: 'entities', label: 'Entities', icon: Users },
    { id: 'graph', label: 'Investigation Graph', icon: Network },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
    { id: 'clusters', label: 'Clusters', icon: Layers },
    { id: 'leads', label: 'Leads', icon: FileText },
    { id: 'cases', label: 'Cases', icon: FolderKanban },
    { id: 'evaluation', label: 'Model Evaluation', icon: Activity },
    { id: 'logs', label: 'System Logs', icon: Terminal },
  ];

  return (
    <nav className="bg-surface-100 border-b border-surface-300 sticky top-0 z-50 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand Header */}
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-brand-600 to-brand-700 p-2 rounded-lg shadow-lg shadow-brand-200/30">
            <ShieldAlert className="w-6 h-6 text-brand-900" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-brand-900 flex items-center gap-2">
              KRISHIGUARD
              <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-brand-100 text-brand-600 border border-cyan-800">
                OFFLINE FORENSIC
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-warning-950/80 text-warning-600 border border-warning-800/80 animate-pulse">
                SYNTHETIC / DEMO DATA
              </span>
            </h1>
            <p className="text-xs text-content-500">Offline Bitcoin Investigation & AI Analytics</p>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="flex flex-wrap items-center gap-1 overflow-x-auto pb-1 md:pb-0">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-500/10 text-brand-600 border border-brand-500/30 shadow-sm'
                    : 'text-content-500 hover:text-brand-900 hover:bg-surface-200'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-content-500'}`} />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
};
