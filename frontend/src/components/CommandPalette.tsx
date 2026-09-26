import React, { useEffect, useRef, useState } from 'react';
import { Search, Network, AlertTriangle, FileText, FolderKanban, Download, RefreshCw, Moon, Columns, Terminal } from 'lucide-react';
import { usePreferences } from '../context/PreferencesContext';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (tab: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, onNavigate }) => {
  const { theme, setTheme, density, setDensity, sidebarCollapsed, setSidebarCollapsed } = usePreferences();
  const [searchQuery, setSearchQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setSearchQuery('');
      setTimeout(() => inputRef.current?.focus(), 10);
    }
  }, [isOpen]);

  // Handle keyboard shortcuts (Ctrl+K to open, Esc to close is handled in App)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const allCommands = [
    { id: 'search-tx', label: 'Search transaction...', group: 'SEARCH', icon: Search, action: () => alert('Search TX: ' + searchQuery) },
    { id: 'search-wallet', label: 'Search wallet...', group: 'SEARCH', icon: Search, action: () => alert('Search Wallet: ' + searchQuery) },
    { id: 'search-ip', label: 'Search IP...', group: 'SEARCH', icon: Search, action: () => alert('Search IP: ' + searchQuery) },
    { id: 'search-entity', label: 'Search entity...', group: 'SEARCH', icon: Search, action: () => alert('Search Entity: ' + searchQuery) },
    
    { id: 'nav-graph', label: 'Open Investigation Graph', group: 'INVESTIGATE', icon: Network, action: () => onNavigate('graph') },
    { id: 'nav-anomalies', label: 'Open Anomalies', group: 'INVESTIGATE', icon: AlertTriangle, action: () => onNavigate('anomalies') },
    { id: 'nav-leads', label: 'Open Priority Leads', group: 'INVESTIGATE', icon: FileText, action: () => onNavigate('leads') },
    { id: 'nav-cases', label: 'Open Cases', group: 'INVESTIGATE', icon: FolderKanban, action: () => onNavigate('cases') },
    
    { id: 'action-export', label: 'Export current data', group: 'ACTIONS', icon: Download, action: () => alert('Exporting data...') },
    { id: 'action-refresh', label: 'Refresh analysis', group: 'ACTIONS', icon: RefreshCw, action: () => alert('Refreshing analysis...') },
    
    { id: 'sys-theme', label: `Toggle theme (${theme})`, group: 'SYSTEM', icon: Moon, action: () => setTheme(theme === 'dark' ? 'light' : 'dark') },
    { id: 'sys-density', label: `Toggle density (${density})`, group: 'SYSTEM', icon: Columns, action: () => setDensity(density === 'compact' ? 'comfortable' : 'compact') },
    { id: 'sys-sidebar', label: 'Toggle sidebar', group: 'SYSTEM', icon: Columns, action: () => setSidebarCollapsed(!sidebarCollapsed) },
    { id: 'sys-logs', label: 'View system logs', group: 'SYSTEM', icon: Terminal, action: () => onNavigate('logs') },
  ];

  const filteredCommands = allCommands.filter(cmd => 
    cmd.label.toLowerCase().includes(searchQuery.toLowerCase()) || 
    cmd.group.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchQuery]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev < filteredCommands.length - 1 ? prev + 1 : prev));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : prev));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          handleAction(filteredCommands[selectedIndex].action);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, filteredCommands, selectedIndex]);

  if (!isOpen) return null;

  const handleAction = (action: () => void) => {
    action();
    onClose();
  };

  // Group filtered commands
  const groups = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.group]) acc[cmd.group] = [];
    acc[cmd.group].push(cmd);
    return acc;
  }, {} as Record<string, typeof allCommands>);

  let globalIndex = 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
      <div className="absolute inset-0 bg-content-700/40 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative w-full max-w-2xl bg-surface-50 rounded-xl shadow-2xl border border-surface-300 overflow-hidden flex flex-col max-h-[70vh]">
        
        {/* Search Input */}
        <div className="flex items-center px-4 py-4 border-b border-surface-300">
          <Search className="w-5 h-5 text-content-400 mr-3" />
          <input
            ref={inputRef}
            type="text"
            className="flex-1 bg-transparent border-none outline-none text-content-700 placeholder:text-content-300 text-lg"
            placeholder="Search TXID, wallet, IP, entity..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="text-xs text-content-400 font-mono bg-surface-200 px-2 py-1 rounded">ESC to close</div>
        </div>

        {/* Command List */}
        <div className="overflow-y-auto flex-1 p-2">
          {Object.keys(groups).length === 0 ? (
            <div className="py-8 text-center text-sm text-content-400">
              No matching commands or entities found for "{searchQuery}".
            </div>
          ) : (
            Object.entries(groups).map(([groupName, commands]) => (
              <div key={groupName} className="mb-4">
                <div className="px-3 py-1.5 text-xs font-semibold text-content-400 tracking-wider">{groupName}</div>
                {commands.map((cmd) => {
                  const currentIndex = globalIndex++;
                  const Icon = cmd.icon;
                  const isSelected = currentIndex === selectedIndex;
                  return (
                    <button 
                      key={cmd.id}
                      onClick={() => handleAction(cmd.action)} 
                      onMouseEnter={() => setSelectedIndex(currentIndex)}
                      className={`w-full text-left flex items-center px-3 py-2 text-sm rounded-md transition-all ${
                        isSelected 
                          ? 'bg-brand-600 text-white' 
                          : 'text-content-600 hover:bg-surface-100'
                      }`}
                    >
                      <Icon className={`w-4 h-4 mr-3 ${isSelected ? 'text-brand-200' : 'text-content-400'}`} /> 
                      {cmd.label}
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
