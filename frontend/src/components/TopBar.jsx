import { useState } from 'react';
import { Search, Bell, Moon, Sun, User, Shield, ChevronDown } from 'lucide-react';

export default function TopBar({ title, subtitle }) {
  const [darkMode, setDarkMode] = useState(true);
  const [searchVal, setSearchVal] = useState('');

  return (
    <header className="h-16 bg-navy-900 border-b border-navy-700 flex items-center px-6 gap-4">
      {/* Page Title */}
      <div className="flex-1">
        <h2 className="text-white font-semibold text-base leading-tight">{title}</h2>
        {subtitle && <p className="text-slate-500 text-xs mt-0.5">{subtitle}</p>}
      </div>

      {/* Search */}
      <div className="relative hidden md:block">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
        <input
          type="text"
          value={searchVal}
          onChange={e => setSearchVal(e.target.value)}
          placeholder="Search verifications..."
          className="bg-navy-850 border border-navy-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-300
                     placeholder-slate-600 focus:outline-none focus:border-indigo-500 w-56 transition-all"
        />
      </div>

      {/* Status Pill */}
      <div className="hidden sm:flex items-center gap-2 bg-navy-850 border border-navy-700 rounded-full px-3 py-1.5">
        <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]" />
        <span className="text-xs text-emerald-400 font-medium">Systems Normal</span>
      </div>

      {/* Theme Toggle */}
      <button
        onClick={() => setDarkMode(!darkMode)}
        className="w-9 h-9 flex items-center justify-center rounded-lg bg-navy-850 border border-navy-700
                   text-slate-400 hover:text-slate-200 hover:border-navy-600 transition-all"
        title="Toggle theme"
      >
        {darkMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
      </button>

      {/* Notification */}
      <button className="w-9 h-9 flex items-center justify-center rounded-lg bg-navy-850 border border-navy-700
                         text-slate-400 hover:text-slate-200 hover:border-navy-600 transition-all relative">
        <Bell className="w-4 h-4" />
        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-400 rounded-full" />
      </button>

      {/* User */}
      <button className="flex items-center gap-2 bg-navy-850 border border-navy-700 rounded-lg px-3 py-1.5
                         text-slate-300 hover:text-white hover:border-navy-600 transition-all">
        <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center">
          <User className="w-3.5 h-3.5 text-indigo-400" />
        </div>
        <span className="text-sm font-medium hidden sm:block">Admin</span>
        <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
      </button>
    </header>
  );
}
