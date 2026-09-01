import { useState, useRef, useCallback } from 'react';
import {
  Upload, FileText, Image, X, ScanLine, ChevronRight,
  CheckCircle2, Circle, Loader2, AlertTriangle, RotateCcw,
  Shield, Eye, FileSearch, Database, Cpu, Layers,
  Activity, AlertCircle, Download, User, Camera, TestTube2
} from 'lucide-react';
import { verifyDocument } from '../api/client';
import SignalBadge from '../components/SignalBadge';

// ─── Pipeline steps (shown during analysis) ─────────────────────────────────
const PIPELINE_STEPS = [
  { id: 'validation',       label: 'File Validation',          icon: Shield },
  { id: 'classification',   label: 'Document Classification',  icon: FileSearch },
  { id: 'ocr',              label: 'OCR Extraction',           icon: Eye },
  { id: 'vision',           label: 'Computer Vision Analysis', icon: Layers },
  { id: 'tampering',        label: 'Tampering Analysis',       icon: AlertCircle },
  { id: 'metadata',         label: 'Metadata Analysis',        icon: Database },
  { id: 'qr',               label: 'QR Analysis',              icon: Cpu },
  { id: 'risk',             label: 'Risk Engine',              icon: Activity },
  { id: 'report',           label: 'Report Generation',        icon: FileText },
];

const SIGNAL_LABELS = {
  ocr_consistency: 'OCR Consistency',
  image_integrity: 'Image Integrity',
  tampering:       'Tampering Detection',
  metadata:        'Metadata Analysis',
  qr:              'QR Analysis',
  face_match:      'Identity Match',
};

// ─── Trust Score Circle ───────────────────────────────────────────────────────
function TrustScoreCircle({ score, riskLevel }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (score / 100) * circumference;

  const colorMap = {
    LOW:    { stroke: '#10b981', text: 'text-emerald-400', bg: 'text-emerald-400' },
    MEDIUM: { stroke: '#f59e0b', text: 'text-amber-400',   bg: 'text-amber-400' },
    HIGH:   { stroke: '#ef4444', text: 'text-red-400',     bg: 'text-red-400' },
  };
  const colors = colorMap[riskLevel] || colorMap.MEDIUM;

  return (
    <div className="relative flex items-center justify-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* Track */}
        <circle
          cx="70" cy="70" r={radius}
          fill="none" stroke="#1a2744" strokeWidth="10"
        />
        {/* Score arc */}
        <circle
          cx="70" cy="70" r={radius}
          fill="none"
          stroke={colors.stroke}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{
            transform: 'rotate(-90deg)',
            transformOrigin: '50% 50%',
            transition: 'stroke-dashoffset 1.2s ease-out',
            filter: `drop-shadow(0 0 8px ${colors.stroke}66)`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold ${colors.text}`}>{score}</span>
        <span className="text-slate-500 text-xs font-medium">/ 100</span>
      </div>
    </div>
  );
}

// ─── Processing Screen ────────────────────────────────────────────────────────
function ProcessingScreen({ currentStep }) {
  return (
    <div className="max-w-lg mx-auto animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-16 h-16 mx-auto mb-4 bg-indigo-600/10 border border-indigo-500/30 rounded-full
                        flex items-center justify-center">
          <Shield className="w-8 h-8 text-indigo-400 animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Analyzing Document</h2>
        <p className="text-slate-400 text-sm">Running forensic pipeline — please wait</p>
      </div>

      <div className="card space-y-2">
        {PIPELINE_STEPS.map((step, i) => {
          const Icon = step.icon;
          const isComplete = i < currentStep;
          const isCurrent = i === currentStep;
          const isWaiting = i > currentStep;

          return (
            <div
              key={step.id}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 ${
                isCurrent ? 'bg-indigo-600/10 border border-indigo-500/20' :
                isComplete ? 'bg-emerald-500/5' : ''
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                isComplete ? 'bg-emerald-500/20' :
                isCurrent  ? 'bg-indigo-500/20' : 'bg-navy-700'
              }`}>
                {isComplete ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
                ) : (
                  <Circle className="w-3.5 h-3.5 text-slate-600" />
                )}
              </div>
              <Icon className={`w-4 h-4 flex-shrink-0 ${
                isComplete ? 'text-emerald-400' :
                isCurrent  ? 'text-indigo-400' : 'text-slate-600'
              }`} />
              <span className={`text-sm font-medium ${
                isComplete ? 'text-emerald-300' :
                isCurrent  ? 'text-indigo-300 step-analyzing' :
                             'text-slate-600'
              }`}>
                {step.label}
              </span>
              <span className="ml-auto text-xs font-mono">
                {isComplete ? (
                  <span className="text-emerald-500">COMPLETE</span>
                ) : isCurrent ? (
                  <span className="text-indigo-400">ANALYZING</span>
                ) : (
                  <span className="text-slate-700">WAITING</span>
                )}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Result Screen ────────────────────────────────────────────────────────────
function ResultScreen({ result, onReset, filePreview }) {
  const { trust_score, risk_level, document_type, ocr, signals, reasons, processing_time, verification_id } = result;

  const riskColors = {
    LOW:    'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    MEDIUM: 'text-amber-400   bg-amber-500/10   border-amber-500/30',
    HIGH:   'text-red-400     bg-red-500/10     border-red-500/30',
  };

  const handlePrint = () => window.print();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Verification Report</h2>
          <p className="text-slate-500 text-sm mt-0.5">
            ID: <span className="font-mono text-indigo-400">{verification_id}</span>
            &nbsp;·&nbsp; {processing_time}s processing time
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handlePrint} className="btn-secondary text-sm">
            <Download className="w-4 h-4" />
            Export Report
          </button>
          <button onClick={onReset} className="btn-secondary text-sm">
            <RotateCcw className="w-4 h-4" />
            New Scan
          </button>
        </div>
      </div>

      {/* ── Score + Preview ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Score card */}
        <div className="card flex flex-col items-center text-center glow-border">
          <p className="text-slate-400 text-sm font-medium mb-4">Trust Score</p>
          <TrustScoreCircle score={trust_score} riskLevel={risk_level} />
          <div className={`mt-4 px-4 py-1.5 rounded-full border text-sm font-bold ${riskColors[risk_level]}`}>
            {risk_level} RISK
          </div>
          <p className="text-slate-500 text-xs mt-3">
            Document: <span className="text-slate-300 font-mono">{document_type}</span>
          </p>
        </div>

        {/* Document preview */}
        <div className="card lg:col-span-2">
          <p className="text-slate-400 text-sm font-medium mb-3">Document Preview</p>
          {filePreview ? (
            <img
              src={filePreview}
              alt="Document preview"
              className="rounded-lg border border-navy-600 max-h-56 w-full object-contain bg-navy-900"
            />
          ) : (
            <div className="h-36 bg-navy-900 rounded-lg border border-navy-700 flex items-center justify-center">
              <FileText className="w-12 h-12 text-slate-700" />
            </div>
          )}

          {/* OCR fields */}
          {ocr?.available && (
            <div className="mt-4 grid grid-cols-2 gap-3">
              {[
                { label: 'Name',         val: ocr.name },
                { label: 'Date of Birth',val: ocr.dob },
                { label: 'ID Number',    val: ocr.id_number },
                { label: 'Document Type',val: ocr.document_type },
              ].map(({ label, val }) => (
                <div key={label} className="bg-navy-900 rounded-lg px-3 py-2.5 border border-navy-700">
                  <p className="text-slate-500 text-xs mb-0.5">{label}</p>
                  <p className="text-slate-200 text-sm font-medium font-mono">
                    {val || <span className="text-slate-600 font-sans italic text-xs">Not detected</span>}
                  </p>
                </div>
              ))}
            </div>
          )}
          {!ocr?.available && (
            <p className="mt-3 text-slate-500 text-sm italic">
              OCR could not reliably extract text.{ocr?.error ? ` (${ocr.error})` : ''}
            </p>
          )}
        </div>
      </div>

      {/* ── Forensic Signals ── */}
      <div className="card">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          Forensic Signal Analysis
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {signals && Object.entries(signals).map(([key, sig]) => (
            <div
              key={key}
              className={`rounded-lg border px-3 py-3 ${
                sig.status === 'PASS'          ? 'border-emerald-500/20 bg-emerald-500/5' :
                sig.status === 'WARNING'       ? 'border-amber-500/20   bg-amber-500/5'   :
                sig.status === 'SUSPICIOUS'    ? 'border-red-500/20     bg-red-500/5'     :
                                                 'border-navy-700       bg-navy-850'
              }`}
            >
              <p className="text-slate-400 text-xs mb-1.5">{SIGNAL_LABELS[key] || key}</p>
              <SignalBadge status={sig.status} />
              {sig.details && (
                <p className="text-slate-500 text-xs mt-1.5 leading-tight">{sig.details}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── Why This Score ── */}
      {reasons && reasons.length > 0 && (
        <div className="card">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Why This Score?
          </h3>
          <div className="space-y-2">
            {reasons.map((r, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 px-3 py-2.5 rounded-lg border ${
                  r.impact < -10  ? 'border-red-500/20 bg-red-500/5' :
                  r.impact < 0    ? 'border-amber-500/20 bg-amber-500/5' :
                                    'border-navy-700 bg-navy-850'
                }`}
              >
                <div className={`mt-0.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  r.impact < -10  ? 'bg-red-400' :
                  r.impact < 0    ? 'bg-amber-400' : 'bg-emerald-400'
                }`} />
                <p className="text-sm text-slate-300 flex-1">{r.reason}</p>
                {r.impact !== 0 && (
                  <span className={`text-xs font-mono font-bold flex-shrink-0 ${
                    r.impact < 0 ? 'text-red-400' : 'text-emerald-400'
                  }`}>
                    {r.impact > 0 ? '+' : ''}{r.impact}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main ScanVerify Page ─────────────────────────────────────────────────────
export default function ScanVerify() {
  const [phase, setPhase] = useState('upload'); // upload | processing | result
  const [dragOver, setDragOver] = useState(false);
  const [docFile, setDocFile] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const [docPreview, setDocPreview] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);
  const selfieInputRef = useRef(null);

  const handleFile = useCallback((file) => {
    const allowed = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'application/pdf'];
    if (!allowed.includes(file.type)) {
      setError(`Unsupported file type: ${file.type}. Please upload PNG, JPG, WEBP, or PDF.`);
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB.');
      return;
    }
    setError(null);
    setDocFile(file);
    if (file.type !== 'application/pdf') {
      const url = URL.createObjectURL(file);
      setDocPreview(url);
    } else {
      setDocPreview(null);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const loadDemoFile = async (filename, label) => {
    try {
      // Demo files served from backend test_data
      const response = await fetch(`http://localhost:8000/demo/${filename}`);
      if (!response.ok) throw new Error('Demo file not available');
      const blob = await response.blob();
      const file = new File([blob], filename, { type: blob.type || 'image/png' });
      handleFile(file);
    } catch (e) {
      // Fallback: create a synthetic file client-side as placeholder
      setError(`Demo file not found on server. Please start the backend and regenerate fixtures.`);
    }
  };

  const handleAnalyze = async () => {
    if (!docFile) return;
    setPhase('processing');
    setCurrentStep(0);
    setError(null);

    // Simulate step progression while waiting for backend
    const totalSteps = PIPELINE_STEPS.length;
    let step = 0;

    // Advance steps every ~500ms until near end; final steps wait for actual response
    const stepInterval = setInterval(() => {
      step++;
      if (step < totalSteps - 2) {
        setCurrentStep(step);
      } else {
        clearInterval(stepInterval);
      }
    }, 500);

    try {
      const data = await verifyDocument(docFile, selfieFile || null);

      clearInterval(stepInterval);

      // Complete remaining steps quickly
      for (let s = step; s < totalSteps; s++) {
        setCurrentStep(s);
        await new Promise(r => setTimeout(r, 200));
      }

      setResult(data);
      setPhase('result');
    } catch (err) {
      clearInterval(stepInterval);
      const msg = err?.response?.data?.detail || err.message || 'Analysis failed';
      setError(msg);
      setPhase('upload');
    }
  };

  const handleReset = () => {
    setPhase('upload');
    setDocFile(null);
    setSelfieFile(null);
    setDocPreview(null);
    setResult(null);
    setError(null);
    setCurrentStep(0);
  };

  if (phase === 'processing') {
    return (
      <div className="p-6">
        <ProcessingScreen currentStep={currentStep} />
      </div>
    );
  }

  if (phase === 'result' && result) {
    return (
      <div className="p-6">
        <ResultScreen result={result} onReset={handleReset} filePreview={docPreview} />
      </div>
    );
  }

  // Upload phase
  return (
    <div className="p-6 space-y-6">
      {/* Demo Test Cases */}
      <div className="card border border-indigo-500/20 bg-indigo-500/5">
        <div className="flex items-center gap-2 mb-3">
          <TestTube2 className="w-4 h-4 text-indigo-400" />
          <h3 className="text-white font-semibold text-sm">Demo Test Cases</h3>
          <span className="badge-na ml-1">SYNTHETIC — NOT REAL DOCUMENTS</span>
        </div>
        <p className="text-slate-400 text-xs mb-3">
          Quick-load synthetic demo fixtures to demonstrate the forensic pipeline.
          Results are from actual analysis — not hardcoded.
        </p>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => loadDemoFile('clean_pan.png', 'Clean PAN (Demo)')}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            Clean Test Document
            <span className="text-slate-500 text-xs ml-1">(expect HIGH score)</span>
          </button>
          <button
            onClick={() => loadDemoFile('tampered_aadhaar.png', 'Tampered Aadhaar (Demo)')}
            className="btn-secondary text-xs py-1.5 px-3"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
            Tampered Test Document
            <span className="text-slate-500 text-xs ml-1">(expect LOWER score)</span>
          </button>
        </div>
      </div>

      {/* Upload Area */}
      <div className="card">
        <h3 className="text-white font-semibold mb-1 flex items-center gap-2">
          <ScanLine className="w-4 h-4 text-indigo-400" />
          Scan & Verify Document
        </h3>
        <p className="text-slate-500 text-xs mb-5">
          Upload an identity document for forensic analysis
        </p>

        {/* Drop Zone */}
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`
            relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer
            transition-all duration-200
            ${dragOver
              ? 'border-indigo-500 bg-indigo-600/10 drop-zone-active'
              : docFile
              ? 'border-emerald-500/50 bg-emerald-500/5'
              : 'border-navy-600 hover:border-indigo-500/50 hover:bg-navy-800/60'
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".png,.jpg,.jpeg,.webp,.pdf"
            className="hidden"
            onChange={e => e.target.files[0] && handleFile(e.target.files[0])}
          />

          {docFile ? (
            <div className="space-y-3">
              {docPreview ? (
                <img
                  src={docPreview}
                  alt="Preview"
                  className="max-h-48 mx-auto rounded-lg border border-navy-600 object-contain"
                  onClick={e => e.stopPropagation()}
                />
              ) : (
                <FileText className="w-16 h-16 mx-auto text-indigo-400" />
              )}
              <div>
                <p className="text-white font-medium">{docFile.name}</p>
                <p className="text-slate-500 text-sm">{(docFile.size / 1024).toFixed(1)} KB</p>
              </div>
              <button
                onClick={e => { e.stopPropagation(); setDocFile(null); setDocPreview(null); }}
                className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-red-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" /> Remove
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="w-14 h-14 mx-auto bg-navy-800 border border-navy-600 rounded-xl
                              flex items-center justify-center">
                <Upload className="w-7 h-7 text-slate-500" />
              </div>
              <div>
                <p className="text-white font-medium">Drag & drop document here</p>
                <p className="text-slate-500 text-sm mt-1">or click to browse</p>
                <p className="text-slate-600 text-xs mt-2">PNG · JPG · JPEG · WEBP · PDF · Max 10MB</p>
              </div>
            </div>
          )}
        </div>

        {/* Selfie (optional) */}
        <div className="mt-4">
          <button
            onClick={() => selfieInputRef.current?.click()}
            className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <Camera className="w-4 h-4" />
            {selfieFile ? (
              <span className="text-emerald-400">{selfieFile.name} attached</span>
            ) : (
              <span>Upload Selfie (Optional — for identity match)</span>
            )}
          </button>
          <input
            ref={selfieInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={e => e.target.files[0] && setSelfieFile(e.target.files[0])}
          />
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 flex items-start gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* Pipeline info */}
        <div className="mt-5 bg-navy-900 border border-navy-700 rounded-lg px-4 py-3">
          <p className="text-slate-500 text-xs font-medium flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
            Analysis pipeline:
            <span className="text-slate-400">
              OCR → Computer Vision → Forensics → Metadata → Risk Engine
            </span>
          </p>
        </div>

        {/* Analyze button */}
        <div className="mt-5 flex justify-end">
          <button
            onClick={handleAnalyze}
            disabled={!docFile}
            className="btn-primary text-base px-8 py-3"
          >
            <ScanLine className="w-5 h-5" />
            Analyze Document
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
