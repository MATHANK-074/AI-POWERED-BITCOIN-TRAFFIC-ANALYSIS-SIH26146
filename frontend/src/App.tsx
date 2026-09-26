
import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { DataIngestion } from './pages/DataIngestion';
import { Transactions } from './pages/Transactions';
import { Entities } from './pages/Entities';
import { InvestigationGraph } from './pages/InvestigationGraph';
import { Anomalies } from './pages/Anomalies';
import { Clusters } from './pages/Clusters';
import { Leads } from './pages/Leads';
import { Cases } from './pages/Cases';
import { Evaluation } from './pages/Evaluation';
import { SystemLogs } from './pages/SystemLogs';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <Overview onNavigate={setActiveTab} />;
      case 'ingestion': return <DataIngestion />;
      case 'transactions': return <Transactions />;
      case 'entities': return <Entities />;
      case 'graph': return <InvestigationGraph />;
      case 'anomalies': return <Anomalies />;
      case 'clusters': return <Clusters />;
      case 'leads': return <Leads />;
      case 'cases': return <Cases />;
      case 'evaluation': return <Evaluation />;
      case 'logs': return <SystemLogs />;
      default: return <Overview onNavigate={setActiveTab} />;
    }
  };

  return (
    <div className='min-h-screen bg-surface-50 text-content-700 flex flex-col font-sans'>
      <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <div className='flex flex-1 overflow-hidden'>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} isOpen={sidebarOpen} />
        <main className='flex-1 overflow-y-auto p-4 md:p-8 bg-surface-50'>
          <div className='max-w-7xl mx-auto'>
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;

