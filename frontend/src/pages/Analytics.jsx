import { useState, useEffect } from 'react';
import { BarChart2, RefreshCw } from 'lucide-react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { getHistory } from '../api/client';

const RISK_COLORS = { LOW: '#10b981', MEDIUM: '#f59e0b', HIGH: '#ef4444' };
const DOC_COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-900 border border-navy-600 rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.fill || p.color }} className="font-semibold">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

export default function Analytics() {
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

  // Compute chart data
  const riskDist = ['LOW', 'MEDIUM', 'HIGH'].map(level => ({
    name: level,
    value: history.filter(h => h.risk_level === level).length,
  })).filter(d => d.value > 0);

  const docTypeDist = Object.entries(
    history.reduce((acc, h) => {
      acc[h.document_type] = (acc[h.document_type] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const scoreByDate = history.slice(0, 20).reverse().map((h, i) => ({
    name: `#${i + 1}`,
    score: h.trust_score,
    risk: h.risk_level,
  }));

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-64 gap-3 text-slate-600">
        <BarChart2 className="w-10 h-10" />
        <p>No data yet — run some verifications first</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-bold text-lg">Analytics</h2>
        <button onClick={load} className="btn-secondary text-sm">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Risk Distribution */}
        <div className="card">
          <h3 className="text-white font-semibold mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={riskDist} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {riskDist.map((entry) => (
                  <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Document Type Distribution */}
        <div className="card">
          <h3 className="text-white font-semibold mb-4">Document Types</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={docTypeDist}>
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="Count">
                {docTypeDist.map((_, i) => (
                  <Cell key={i} fill={DOC_COLORS[i % DOC_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Trust Score Trend */}
        <div className="card lg:col-span-2">
          <h3 className="text-white font-semibold mb-4">Trust Score Trend (last 20)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={scoreByDate}>
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="score" name="Trust Score">
                {scoreByDate.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.score >= 80 ? '#10b981' : entry.score >= 50 ? '#f59e0b' : '#ef4444'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
