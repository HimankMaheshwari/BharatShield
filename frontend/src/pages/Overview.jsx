import { useState, useEffect } from 'react';
import {
  FileText, TrendingUp, ShieldCheck, ShieldAlert, BarChart2,
  RefreshCw, Clock
} from 'lucide-react';
import { getHistory } from '../api/client';

function StatCard({ icon: Icon, label, value, color = 'text-white', sub }) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <span className="text-slate-400 text-sm">{label}</span>
        <div className={`w-8 h-8 rounded-lg bg-navy-700 flex items-center justify-center`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
      </div>
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-slate-500 text-xs">{sub}</p>}
    </div>
  );
}

export default function Overview({ onNavigate }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getHistory();
      setHistory(data.history || []);
    } catch {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const total = history.length;
  const verified = history.filter(h => h.risk_level === 'LOW').length;
  const flagged = history.filter(h => h.risk_level === 'HIGH').length;
  const avgScore = total > 0
    ? Math.round(history.reduce((a, b) => a + b.trust_score, 0) / total)
    : '--';

  const riskBadge = (level) => {
    if (level === 'LOW') return 'badge-pass';
    if (level === 'MEDIUM') return 'badge-warning';
    return 'badge-suspicious';
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText} label="Documents Scanned" value={total} color="text-indigo-400" sub="All time" />
        <StatCard icon={ShieldCheck} label="Verified (Low Risk)" value={verified} color="text-emerald-400" />
        <StatCard icon={ShieldAlert} label="Flagged (High Risk)" value={flagged} color="text-red-400" />
        <StatCard icon={TrendingUp} label="Avg Trust Score" value={avgScore} color="text-amber-400" sub="Out of 100" />
      </div>

      {/* Quick action */}
      <div className="card border border-indigo-500/20 bg-gradient-to-br from-indigo-600/10 to-navy-850">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold text-lg">Start Document Verification</h3>
            <p className="text-slate-400 text-sm mt-1">
              Upload an identity document to run the full forensic analysis pipeline.
            </p>
          </div>
          <button
            onClick={() => onNavigate('scan')}
            className="btn-primary text-sm whitespace-nowrap"
          >
            <FileText className="w-4 h-4" />
            Scan & Verify
          </button>
        </div>
      </div>

      {/* Recent verifications */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            Recent Verifications
          </h3>
          <button onClick={load} className="btn-secondary text-xs py-1.5">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-32 text-slate-600">
            <RefreshCw className="w-5 h-5 animate-spin" />
          </div>
        ) : history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-slate-600 gap-2">
            <FileText className="w-8 h-8" />
            <p className="text-sm">No verifications yet — run your first scan!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700">
                  {['ID', 'Document', 'Score', 'Risk', 'Date'].map(h => (
                    <th key={h} className="text-left text-slate-500 font-medium pb-2 pr-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800">
                {history.slice(0, 10).map(row => (
                  <tr key={row.id} className="hover:bg-navy-800/40 transition-colors">
                    <td className="py-2.5 pr-4 font-mono text-indigo-400 text-xs">{row.verification_id}</td>
                    <td className="py-2.5 pr-4 text-slate-300">{row.document_type}</td>
                    <td className="py-2.5 pr-4 font-bold text-white">{row.trust_score}</td>
                    <td className="py-2.5 pr-4">
                      <span className={riskBadge(row.risk_level)}>{row.risk_level}</span>
                    </td>
                    <td className="py-2.5 text-slate-500 text-xs">
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
