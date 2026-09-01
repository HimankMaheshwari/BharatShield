import { Shield, Eye, Brain, Lock, AlertTriangle, CheckCircle2 } from 'lucide-react';

const Feature = ({ icon: Icon, color, title, items }) => (
  <div className="card">
    <div className={`w-9 h-9 rounded-lg ${color} flex items-center justify-center mb-3`}>
      <Icon className="w-5 h-5 text-white" />
    </div>
    <h3 className="text-white font-semibold mb-2">{title}</h3>
    <ul className="text-slate-400 text-sm space-y-1.5">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
          {item}
        </li>
      ))}
    </ul>
  </div>
);

export default function About() {
  const implemented = [
    'ELA (Error Level Analysis) for JPEG compression inconsistency detection',
    'Edge analysis via OpenCV Laplacian/Canny for region sharpness variance',
    'EXIF/metadata extraction — software, timestamps, camera info',
    'Deterministic weighted risk engine (evidence-based deductions)',
    'Rule-based document classification (Aadhaar, PAN, Passport, DL)',
    'pytesseract OCR with graceful fallback if Tesseract not installed',
    'OpenCV QR code detection and decoding',
    'SQLite-backed verification history (aiosqlite)',
    'Synthetic demo fixtures (clean + tampered) for reliable demonstration',
    'Explainable results — every deduction includes reason and impact',
  ];

  const future = [
    'Actual government database integration (UIDAI, Income Tax API)',
    'Face embedding model (e.g., ArcFace/FaceNet) for real identity match',
    'ML-based document classifier replacing regex rules',
    'Real Aadhaar QR signature verification (XML + RSA)',
    'Blockchain audit trail for verification records',
    'Multi-language OCR support (regional scripts)',
    'Liveness detection for selfie verification',
    'Enterprise SSO / API key authentication',
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="card border border-indigo-500/20 bg-gradient-to-br from-indigo-600/10 to-navy-850">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-indigo-600/20 border border-indigo-500/40 rounded-xl flex items-center justify-center">
            <Shield className="w-8 h-8 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">BharatShield</h1>
            <p className="text-indigo-400 font-medium">AI-Powered Digital Trust for Bharat</p>
            <p className="text-slate-400 text-sm mt-1">Hackathon MVP — v1.0.0</p>
          </div>
        </div>
        <p className="text-slate-300 text-sm mt-5 leading-relaxed">
          BharatShield is an AI-powered identity and document fraud detection platform that analyzes
          uploaded identity documents for OCR inconsistencies, visual anomalies, tampering indicators,
          metadata anomalies, and QR signals — combining these into an explainable trust/risk score.
        </p>
      </div>

      {/* Pipeline features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Feature
          icon={Eye}
          color="bg-indigo-600"
          title="OCR Extraction"
          items={['pytesseract with confidence scoring', 'Document type classification', 'Field extraction: name, DOB, ID, address', 'Graceful fallback if Tesseract unavailable']}
        />
        <Feature
          icon={Brain}
          color="bg-purple-700"
          title="Image Forensics"
          items={['ELA — JPEG recompression difference', 'Edge inconsistency analysis (Laplacian)', 'Regional compression artifact detection', 'Dimension and aspect ratio validation']}
        />
        <Feature
          icon={Lock}
          color="bg-emerald-700"
          title="Risk Engine"
          items={['Deterministic weighted scoring', 'Every deduction is evidence-based', 'Capped per-category maximum impact', 'Low/Medium/High risk classification']}
        />
      </div>

      {/* Implemented vs Future */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="card">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Actually Implemented
          </h3>
          <ul className="space-y-2">
            {implemented.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-slate-300 text-sm">
                <span className="text-emerald-400 flex-shrink-0 mt-0.5">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
        <div className="card border border-amber-500/20">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Future Production Features
          </h3>
          <ul className="space-y-2">
            {future.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-slate-400 text-sm">
                <span className="text-amber-400 flex-shrink-0 mt-0.5">◯</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card border border-red-500/20 bg-red-500/5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 mt-1 flex-shrink-0" />
          <div>
            <h4 className="text-white font-semibold text-sm mb-1">Important Disclaimer</h4>
            <p className="text-slate-400 text-sm">
              This is a hackathon MVP. It does NOT connect to government databases (UIDAI, Income Tax, etc.).
              Analysis results are based on forensic image analysis only. A flagged document is not evidence
              of fraud — it indicates forensic anomalies that warrant further human review.
              Do NOT use this system as a sole basis for any identity decision.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
