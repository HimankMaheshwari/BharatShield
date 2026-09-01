import { useState, useEffect } from 'react';
import {
  Shield, LayoutDashboard, ScanLine, Clock, BarChart2,
  Plug, Info, ChevronRight, Activity, Zap
} from 'lucide-react';
import { checkHealth } from '../api/client';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'scan', label: 'Scan & Verify', icon: ScanLine },
  { id: 'history', label: 'Verification History', icon: Clock },
  { id: 'analytics', label: 'Analytics', icon: BarChart2 },
  { id: 'api', label: 'API & Integrations', icon: Plug },
  { id: 'about', label: 'About', icon: Info },
];

export default function Sidebar({ activePage, onNavigate }) {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkHealth().then(result => {
      setBackendStatus(result.ok ? 'online' : 'offline');
    });
    const interval = setInterval(() => {
      checkHealth().then(result => {
        setBackendStatus(result.ok ? 'online' : 'offline');
      });
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-64 min-h-screen bg-navy-900 border-r border-navy-700 flex flex-col">
      {/* Logo */}
      <div className="px-5 py-6 border-b border-navy-700">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 bg-indigo-600/20 border border-indigo-500/40 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-white font-bold text-base leading-tight">BharatShield</h1>
            <p className="text-indigo-400 text-xs font-medium">AI-Powered Digital Trust</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={activePage === id ? 'sidebar-link-active w-full text-left' : 'sidebar-link w-full text-left'}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span className="flex-1">{label}</span>
            {activePage === id && <ChevronRight className="w-3.5 h-3.5 opacity-60" />}
          </button>
        ))}
      </nav>

      {/* Backend Status */}
      <div className="px-4 py-4 border-t border-navy-700">
        <div className="bg-navy-850 border border-navy-700 rounded-lg px-3 py-2.5">
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Analysis Engine</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              backendStatus === 'online' ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]' :
              backendStatus === 'offline' ? 'bg-red-400' : 'bg-amber-400 animate-pulse'
            }`} />
            <span className={`text-xs font-semibold ${
              backendStatus === 'online' ? 'text-emerald-400' :
              backendStatus === 'offline' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {backendStatus === 'online' ? 'Online' :
               backendStatus === 'offline' ? 'Offline' : 'Connecting...'}
            </span>
          </div>
          {backendStatus === 'offline' && (
            <p className="text-xs text-red-400/70 mt-1">Start: uvicorn main:app</p>
          )}
        </div>
        <div className="mt-2 flex items-center gap-1.5 px-1">
          <Zap className="w-3 h-3 text-indigo-400" />
          <span className="text-xs text-slate-500">v1.0.0 — Hackathon MVP</span>
        </div>
      </div>
    </aside>
  );
}
