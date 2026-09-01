import { useState, useEffect } from 'react';
import { Clock, RefreshCw, FileText } from 'lucide-react';
import { getHistory } from '../api/client';
import SignalBadge from '../components/SignalBadge';

export default function History() {
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

  const riskBadge = (level) => {
    const map = { LOW: 'PASS', MEDIUM: 'WARNING', HIGH: 'SUSPICIOUS' };
    return map[level] || 'NOT_AVAILABLE';
  };

  return (
    <div className="p-6 space-y-5 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-white font-bold text-lg">Verification History</h2>
          <p className="text-slate-500 text-sm">{history.length} total records</p>
        </div>
        <button onClick={load} className="btn-secondary text-sm">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center h-48 text-slate-600">
            <RefreshCw className="w-6 h-6 animate-spin" />
          </div>
        ) : history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-600 gap-3">
            <Clock className="w-10 h-10" />
            <p>No verifications yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700">
                  {['Verification ID', 'Filename', 'Document Type', 'Score', 'Risk', 'Status', 'Date/Time'].map(h => (
                    <th key={h} className="text-left text-slate-500 font-medium pb-3 pr-4 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800">
                {history.map(row => (
                  <tr key={row.id} className="hover:bg-navy-800/40 transition-colors">
                    <td className="py-3 pr-4 font-mono text-indigo-400 text-xs">{row.verification_id}</td>
                    <td className="py-3 pr-4 text-slate-400 text-xs truncate max-w-32">{row.filename}</td>
                    <td className="py-3 pr-4 text-slate-300">{row.document_type}</td>
                    <td className="py-3 pr-4">
                      <span className={`font-bold text-base ${
                        row.trust_score >= 80 ? 'text-emerald-400' :
                        row.trust_score >= 50 ? 'text-amber-400' : 'text-red-400'
                      }`}>{row.trust_score}</span>
                    </td>
                    <td className="py-3 pr-4">
                      <SignalBadge status={riskBadge(row.risk_level)} />
                    </td>
                    <td className="py-3 pr-4">
                      <SignalBadge status={riskBadge(row.risk_level)} />
                    </td>
                    <td className="py-3 text-slate-500 text-xs whitespace-nowrap">
                      {new Date(row.created_at + 'Z').toLocaleString()}
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
