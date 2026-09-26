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
  Home,
  Database,
  Search,
  Clock,
  Briefcase
} from 'lucide-react';
import { usePreferences } from '../context/PreferencesContext';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean; // Mobile toggle override
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen }) => {
  const { sidebarCollapsed } = usePreferences();

  // We group the existing routes. Routes that don't exist yet but were requested are mocked or mapped to overview if clicked.
  const groups = [
    {
      title: 'INVESTIGATE',
      items: [
        { id: 'overview', label: 'Command Center', icon: Home },
        { id: 'transactions', label: 'Transactions', icon: ListFilter },
        { id: 'entities', label: 'Entities', icon: Users },
        { id: 'graph', label: 'Investigation Graph', icon: Network },
      ]
    },
    {
      title: 'DETECT',
      items: [
        { id: 'anomalies', label: 'Anomalies', icon: AlertTriangle },
        { id: 'clusters', label: 'Clusters', icon: Layers },
        { id: 'leads', label: 'Priority Leads', icon: FileText },
      ]
    },
    {
      title: 'CASEWORK',
      items: [
        { id: 'cases', label: 'Cases', icon: FolderKanban },
      ]
    },
    {
      title: 'ANALYTICS',
      items: [
        { id: 'evaluation', label: 'Model Evaluation', icon: Activity },
        { id: 'ingestion', label: 'Data Ingestion', icon: UploadCloud },
        { id: 'logs', label: 'System Logs', icon: Terminal },
      ]
    }
  ];

  return (
    <aside 
      className={`fixed inset-y-0 left-0 z-40 bg-surface-100 border-r border-surface-300 transform transition-all duration-200 ease-in-out lg:translate-x-0 lg:static flex flex-col ${isOpen ? 'translate-x-0' : '-translate-x-full'} ${sidebarCollapsed ? 'w-16' : 'w-64'}`}
    >
      <div className='flex-1 overflow-y-auto px-3 py-4 custom-scrollbar'>
        <div className='space-y-6'>
          {groups.map((group, idx) => (
            <div key={idx} className="space-y-1">
              {!sidebarCollapsed && (
                <div className="px-3 mb-2 text-[10px] font-bold text-content-400 tracking-wider">
                  {group.title}
                </div>
              )}
              {sidebarCollapsed && (
                <div className="w-full border-b border-surface-300 my-2" />
              )}
              
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    title={sidebarCollapsed ? item.label : undefined}
                    className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-3'} py-2.5 rounded-md text-sm font-medium transition-colors ${isActive ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 dark:text-brand-400 border-l-4 border-brand-600' : 'text-content-500 hover:bg-surface-200 hover:text-content-700 border-l-4 border-transparent'}`}
                  >
                    <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-brand-600 dark:text-brand-400 dark:text-brand-400' : 'text-content-400'}`} />
                    {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Footer Status */}
      <div className={`p-4 border-t border-surface-300 ${sidebarCollapsed ? 'flex justify-center' : ''}`}>
        <div 
          className={`flex items-center ${sidebarCollapsed ? 'justify-center' : 'gap-2'} text-xs font-medium text-content-500`}
          title="Local offline engine active"
        >
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-verified-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-verified-500"></span>
          </span>
          {!sidebarCollapsed && <span>Offline Engine Active</span>}
        </div>
      </div>
    </aside>
  );
};
