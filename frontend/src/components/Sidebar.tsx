
import React from 'react';
import { 
  UploadCloud, 
  ListFilter, 
  Users, 
  Network, 
  AlertTriangle, 
  Layers, 
  FileText, 
  FolderKanban,
  Activity, 
  Terminal,
  Home
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen }) => {
  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: Home },
    { id: 'ingestion', label: 'Data Ingestion', icon: UploadCloud },
    { id: 'transactions', label: 'Transactions', icon: ListFilter },
    { id: 'entities', label: 'Entities', icon: Users },
    { id: 'graph', label: 'Investigation Graph', icon: Network },
    { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
    { id: 'clusters', label: 'Clusters', icon: Layers },
    { id: 'leads', label: 'Investigation Leads', icon: FileText },
    { id: 'cases', label: 'Case Management', icon: FolderKanban },
    { id: 'evaluation', label: 'Model Evaluation', icon: Activity },
    { id: 'logs', label: 'System Logs', icon: Terminal },
  ];

  return (
    <aside className={'fixed inset-y-0 left-0 z-40 w-64 bg-surface-100 border-r border-surface-300 transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:block ' + (isOpen ? 'translate-x-0' : '-translate-x-full')}>
      <div className='h-full overflow-y-auto px-3 py-4'>
        <div className='space-y-1'>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={'w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ' + (isActive ? 'bg-brand-50 text-brand-700 border-l-4 border-brand-600' : 'text-content-500 hover:bg-surface-200 hover:text-content-700 border-l-4 border-transparent')}
              >
                <Icon className={'w-5 h-5 ' + (isActive ? 'text-brand-600' : 'text-content-400')} />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
};

