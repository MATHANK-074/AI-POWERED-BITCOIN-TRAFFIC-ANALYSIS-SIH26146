import React, { useState } from 'react';
import { Bell, Search, Menu, Sun, Moon, Monitor, CheckCircle, AlertCircle } from 'lucide-react';
import { usePreferences } from '../context/PreferencesContext';

interface HeaderProps {
  toggleSidebar: () => void;
  openCommandPalette: () => void;
}

export const Header: React.FC<HeaderProps> = ({ toggleSidebar, openCommandPalette }) => {
  const { theme, setTheme } = usePreferences();
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  
  // Local forensic system health
  const isHealthy = true; // Hardcoded for now, could be dynamic

  return (
    <header className='bg-surface-50 border-b border-surface-300 sticky top-0 z-50 h-14 flex items-center justify-between px-4 shadow-sm'>
      <div className='flex items-center gap-4'>
        <button onClick={toggleSidebar} className='p-1.5 text-content-500 hover:bg-surface-100 rounded-md lg:hidden'>
          <Menu className='w-5 h-5' />
        </button>
        <div className='flex items-center gap-3'>
          <div className='flex items-center justify-center bg-brand-950 p-1 rounded-lg w-8 h-8 overflow-hidden border border-surface-300'>
            <img src="/logo.jpg" alt="Krishiguard Logo" className="w-full h-full object-cover scale-150" />
          </div>
          <div>
            <h1 className='text-base font-bold tracking-tight text-brand-900 dark:text-brand-100 flex items-center gap-2'>
              KRISHIGUARD
              <span className='text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-surface-200 text-content-600 border border-surface-300'>
                OFFLINE FORENSIC
              </span>
            </h1>
          </div>
        </div>
      </div>
      
      <div className='flex items-center gap-3'>
        {/* Global Search Button */}
        <button 
          onClick={openCommandPalette}
          className='hidden md:flex items-center gap-2 px-3 py-1.5 text-sm bg-surface-100 border border-surface-300 rounded-md hover:bg-surface-200 text-content-400 focus:outline-none focus:ring-1 focus:ring-brand-500 w-64'
        >
          <Search className='w-4 h-4' />
          <span className='flex-1 text-left truncate'>Search TXID, wallet, IP...</span>
          <kbd className='hidden lg:inline-block font-sans text-xs bg-surface-200 border border-surface-300 rounded px-1.5 py-0.5 text-content-500'>
            Ctrl K
          </kbd>
        </button>

        {/* System Health */}
        <div className='hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-surface-100 border border-surface-300 rounded-md cursor-pointer hover:bg-surface-200' title="System Health: Local Engine Active">
          {isHealthy ? (
            <CheckCircle className='w-4 h-4 text-verified-500' />
          ) : (
            <AlertCircle className='w-4 h-4 text-warning-500' />
          )}
          <span className='text-xs font-medium text-content-600'>SYSTEM HEALTH</span>
        </div>

        {/* Notifications */}
        <div className='relative'>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className={`p-2 rounded-md relative ${showNotifications ? 'bg-surface-200 text-brand-600 dark:text-brand-400' : 'text-content-500 hover:bg-surface-100'}`} 
            title="Notifications"
          >
            <Bell className='w-5 h-5' />
            <span className='absolute top-1.5 right-1.5 w-2 h-2 bg-critical-500 rounded-full border border-surface-50'></span>
          </button>

          {showNotifications && (
            <div className='absolute right-0 mt-1 w-80 bg-surface-50 border border-surface-300 rounded-md shadow-lg z-50 overflow-hidden'>
              <div className='px-4 py-3 border-b border-surface-200 bg-surface-100 flex justify-between items-center'>
                <h3 className='text-sm font-semibold text-content-700'>Notifications</h3>
                <span className='text-xs text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:text-brand-300 cursor-pointer font-medium'>Mark all as read</span>
              </div>
              <div className='max-h-[300px] overflow-y-auto'>
                <div className='px-4 py-3 border-b border-surface-100 hover:bg-surface-50 cursor-pointer'>
                  <div className='flex items-start gap-3'>
                    <div className='mt-0.5 w-2 h-2 rounded-full bg-critical-500 flex-shrink-0'></div>
                    <div>
                      <p className='text-sm text-content-700 font-medium'>Critical Anomaly Detected</p>
                      <p className='text-xs text-content-500 mt-0.5 line-clamp-2'>New high-risk cluster identified with cyclic flows. Priority score: 98/100.</p>
                      <p className='text-[10px] text-content-400 mt-1 uppercase'>Just now</p>
                    </div>
                  </div>
                </div>
                <div className='px-4 py-3 border-b border-surface-100 hover:bg-surface-50 cursor-pointer'>
                  <div className='flex items-start gap-3'>
                    <div className='mt-0.5 w-2 h-2 rounded-full bg-warning-500 flex-shrink-0'></div>
                    <div>
                      <p className='text-sm text-content-700 font-medium'>Data Ingestion Complete</p>
                      <p className='text-xs text-content-500 mt-0.5 line-clamp-2'>100,000 synthetic records processed successfully in 94 seconds.</p>
                      <p className='text-[10px] text-content-400 mt-1 uppercase'>2 hours ago</p>
                    </div>
                  </div>
                </div>
                <div className='px-4 py-3 hover:bg-surface-50 cursor-pointer'>
                  <div className='flex items-start gap-3'>
                    <div className='mt-0.5 w-2 h-2 rounded-full bg-surface-300 flex-shrink-0'></div>
                    <div>
                      <p className='text-sm text-content-600'>System Update</p>
                      <p className='text-xs text-content-500 mt-0.5 line-clamp-2'>Local DuckDB instance has been vacuumed and optimized.</p>
                      <p className='text-[10px] text-content-400 mt-1 uppercase'>Yesterday</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className='px-4 py-2 border-t border-surface-200 bg-surface-50 text-center'>
                <button className='text-xs text-brand-600 dark:text-brand-400 font-medium hover:text-brand-700 dark:text-brand-300'>View all notifications</button>
              </div>
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <div className='relative'>
          <button 
            onClick={() => setShowThemeMenu(!showThemeMenu)}
            className='p-2 text-content-500 hover:bg-surface-100 rounded-md flex items-center justify-center'
            title="Theme"
          >
            {theme === 'light' && <Sun className='w-5 h-5' />}
            {theme === 'dark' && <Moon className='w-5 h-5' />}
            {theme === 'system' && <Monitor className='w-5 h-5' />}
          </button>
          
          {showThemeMenu && (
            <div className='absolute right-0 mt-1 w-32 bg-surface-50 border border-surface-300 rounded-md shadow-lg py-1 z-50'>
              <button 
                onClick={() => { setTheme('light'); setShowThemeMenu(false); }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-surface-100 ${theme === 'light' ? 'text-brand-600 dark:text-brand-400 font-medium' : 'text-content-600'}`}
              >
                <Sun className='w-4 h-4' /> Light
              </button>
              <button 
                onClick={() => { setTheme('dark'); setShowThemeMenu(false); }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-surface-100 ${theme === 'dark' ? 'text-brand-600 dark:text-brand-400 font-medium' : 'text-content-600'}`}
              >
                <Moon className='w-4 h-4' /> Dark
              </button>
              <button 
                onClick={() => { setTheme('system'); setShowThemeMenu(false); }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-surface-100 ${theme === 'system' ? 'text-brand-600 dark:text-brand-400 font-medium' : 'text-content-600'}`}
              >
                <Monitor className='w-4 h-4' /> System
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Click outside overlay for dropdown menus */}
      {(showThemeMenu || showNotifications) && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => {
            setShowThemeMenu(false);
            setShowNotifications(false);
          }}
        />
      )}
    </header>
  );
};
