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

  if (!isOpen) return null;

  const handleAction = (action: () => void) => {
    action();
    onClose();
  };

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
          
          <div className="mb-4">
            <div className="px-3 py-1.5 text-xs font-semibold text-content-400 tracking-wider">SEARCH</div>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Search className="w-4 h-4 mr-3 text-content-400" /> Search transaction...
            </button>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Search className="w-4 h-4 mr-3 text-content-400" /> Search wallet...
            </button>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Search className="w-4 h-4 mr-3 text-content-400" /> Search IP...
            </button>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Search className="w-4 h-4 mr-3 text-content-400" /> Search entity...
            </button>
          </div>

          <div className="mb-4">
            <div className="px-3 py-1.5 text-xs font-semibold text-content-400 tracking-wider">INVESTIGATE</div>
            <button onClick={() => handleAction(() => onNavigate('graph'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Network className="w-4 h-4 mr-3 text-content-400" /> Open Investigation Graph
            </button>
            <button onClick={() => handleAction(() => onNavigate('anomalies'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <AlertTriangle className="w-4 h-4 mr-3 text-content-400" /> Open Anomalies
            </button>
            <button onClick={() => handleAction(() => onNavigate('leads'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <FileText className="w-4 h-4 mr-3 text-content-400" /> Open Priority Leads
            </button>
            <button onClick={() => handleAction(() => onNavigate('cases'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <FolderKanban className="w-4 h-4 mr-3 text-content-400" /> Open Cases
            </button>
          </div>

          <div className="mb-4">
            <div className="px-3 py-1.5 text-xs font-semibold text-content-400 tracking-wider">ACTIONS</div>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Download className="w-4 h-4 mr-3 text-content-400" /> Export current data
            </button>
            <button className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <RefreshCw className="w-4 h-4 mr-3 text-content-400" /> Refresh analysis
            </button>
          </div>

          <div className="mb-2">
            <div className="px-3 py-1.5 text-xs font-semibold text-content-400 tracking-wider">SYSTEM</div>
            <button onClick={() => handleAction(() => setTheme(theme === 'dark' ? 'light' : 'dark'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Moon className="w-4 h-4 mr-3 text-content-400" /> Toggle theme ({theme})
            </button>
            <button onClick={() => handleAction(() => setDensity(density === 'compact' ? 'comfortable' : 'compact'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Columns className="w-4 h-4 mr-3 text-content-400" /> Toggle density ({density})
            </button>
            <button onClick={() => handleAction(() => setSidebarCollapsed(!sidebarCollapsed))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Columns className="w-4 h-4 mr-3 text-content-400" /> Toggle sidebar
            </button>
            <button onClick={() => handleAction(() => onNavigate('logs'))} className="w-full text-left flex items-center px-3 py-2 text-sm text-content-600 hover:bg-surface-100 rounded-md">
              <Terminal className="w-4 h-4 mr-3 text-content-400" /> View system logs
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};
