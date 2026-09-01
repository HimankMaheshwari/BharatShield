import { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import Overview from './pages/Overview';
import ScanVerify from './pages/ScanVerify';
import History from './pages/History';
import Analytics from './pages/Analytics';
import ApiPage from './pages/ApiPage';
import About from './pages/About';

const PAGE_CONFIG = {
  overview:  { title: 'Overview',              subtitle: 'System dashboard and recent activity' },
  scan:      { title: 'Scan & Verify',          subtitle: 'Upload and analyze identity documents' },
  history:   { title: 'Verification History',   subtitle: 'All past verification results' },
  analytics: { title: 'Analytics',              subtitle: 'Aggregate insights and statistics' },
  api:       { title: 'API & Integrations',     subtitle: 'REST API reference and integration guide' },
  about:     { title: 'About BharatShield',     subtitle: 'Platform overview and feature guide' },
};

export default function App() {
  const [activePage, setActivePage] = useState('overview');

  const { title, subtitle } = PAGE_CONFIG[activePage] || PAGE_CONFIG.overview;

  const renderPage = () => {
    switch (activePage) {
      case 'overview':  return <Overview onNavigate={setActivePage} />;
      case 'scan':      return <ScanVerify />;
      case 'history':   return <History />;
      case 'analytics': return <Analytics />;
      case 'api':       return <ApiPage />;
      case 'about':     return <About />;
      default:          return <Overview onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="flex h-screen bg-navy-950 overflow-hidden">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto bg-navy-950">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
