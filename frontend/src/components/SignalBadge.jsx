/**
 * Signal status badge component.
 * Maps backend signal status → styled badge.
 */
const STATUS_MAP = {
  PASS: {
    cls: 'badge-pass',
    dot: 'bg-emerald-400',
    label: 'PASS',
  },
  WARNING: {
    cls: 'badge-warning',
    dot: 'bg-amber-400',
    label: 'WARNING',
  },
  SUSPICIOUS: {
    cls: 'badge-suspicious',
    dot: 'bg-red-400',
    label: 'SUSPICIOUS',
  },
  NOT_AVAILABLE: {
    cls: 'badge-na',
    dot: 'bg-slate-500',
    label: 'N/A',
  },
};

export default function SignalBadge({ status }) {
  const mapped = STATUS_MAP[status] || STATUS_MAP['NOT_AVAILABLE'];
  return (
    <span className={`${mapped.cls} inline-flex items-center gap-1.5`}>
      <span className={`w-1.5 h-1.5 rounded-full ${mapped.dot}`} />
      {mapped.label}
    </span>
  );
}
