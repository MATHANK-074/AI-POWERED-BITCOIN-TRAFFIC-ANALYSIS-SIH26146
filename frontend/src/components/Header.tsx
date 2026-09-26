
import React from 'react';
import { ShieldAlert, Bell, Search, User, Menu } from 'lucide-react';

interface HeaderProps {
  toggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ toggleSidebar }) => {
  return (
    <header className='bg-surface-50 border-b border-surface-300 sticky top-0 z-50 h-16 flex items-center justify-between px-4 shadow-sm'>
      <div className='flex items-center gap-4'>
        <button onClick={toggleSidebar} className='p-2 text-content-500 hover:bg-surface-100 rounded-md lg:hidden'>
          <Menu className='w-5 h-5' />
        </button>
        <div className='flex items-center gap-3'>
          <div className='bg-brand-600 p-2 rounded-lg'>
            <ShieldAlert className='w-5 h-5 text-white' />
          </div>
          <div>
            <h1 className='text-lg font-bold tracking-tight text-brand-900 flex items-center gap-2'>
              KRISHIGUARD
              <span className='text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-brand-100 text-brand-700 border border-brand-200'>
                WORKSTATION
              </span>
            </h1>
          </div>
        </div>
      </div>
      <div className='flex items-center gap-3'>
        <div className='relative hidden md:block'>
          <Search className='w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-content-400' />
          <input 
            type='text' 
            placeholder='Global search...' 
            className='pl-9 pr-4 py-1.5 text-sm bg-surface-100 border border-surface-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500 w-64'
          />
        </div>
        <button className='p-2 text-content-500 hover:bg-surface-100 rounded-md relative'>
          <Bell className='w-5 h-5' />
          <span className='absolute top-1.5 right-1.5 w-2 h-2 bg-critical-500 rounded-full'></span>
        </button>
        <div className='h-8 w-8 rounded-full bg-surface-200 border border-surface-300 flex items-center justify-center text-content-600 font-medium text-sm ml-2'>
          <User className='w-4 h-4' />
        </div>
      </div>
    </header>
  );
};

