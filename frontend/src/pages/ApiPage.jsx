import { Shield, Code2, Zap, Lock, GitBranch, ExternalLink } from 'lucide-react';

const ENDPOINT_CARD = ({ method, path, desc, body }) => (
  <div className="bg-navy-900 border border-navy-700 rounded-lg p-4">
    <div className="flex items-center gap-2 mb-2">
      <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${
        method === 'POST' ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30' :
                            'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
      }`}>{method}</span>
      <code className="text-sm font-mono text-slate-300">{path}</code>
    </div>
    <p className="text-slate-400 text-sm mb-2">{desc}</p>
    {body && (
      <pre className="text-xs font-mono text-slate-500 bg-navy-950 rounded p-3 overflow-x-auto">
        {body}
      </pre>
    )}
  </div>
);

export default function ApiPage() {
  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h2 className="text-white font-bold text-lg">API & Integrations</h2>
        <p className="text-slate-400 text-sm mt-1">
          REST API running at <code className="text-indigo-400 font-mono">http://localhost:8000</code>
        </p>
      </div>

      <div className="card">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Code2 className="w-4 h-4 text-indigo-400" />
          Available Endpoints
        </h3>
        <div className="space-y-3">
          <ENDPOINT_CARD
            method="POST"
            path="/api/verify"
            desc="Upload a document for full forensic analysis. Returns trust score, risk level, signals, and reasons."
            body={`Content-Type: multipart/form-data\n\ndocument: <file>   (required)\nselfie:   <file>   (optional)`}
          />
          <ENDPOINT_CARD
            method="GET"
            path="/api/history"
            desc="Retrieve verification history from SQLite."
          />
          <ENDPOINT_CARD
            method="GET"
            path="/api/health"
            desc="Health check endpoint."
          />
          <ENDPOINT_CARD
            method="GET"
            path="/api/docs"
            desc="Interactive Swagger UI documentation."
          />
        </div>
      </div>

      <div className="card">
        <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          Example Response
        </h3>
        <pre className="text-xs font-mono text-slate-400 bg-navy-900 rounded-lg p-4 overflow-x-auto leading-relaxed">
{`{
  "verification_id": "A3F2B1C4",
  "document_type": "AADHAAR",
  "trust_score": 82,
  "risk_level": "LOW",
  "ocr": {
    "name": "RAJESH KUMAR",
    "dob": "15/08/1985",
    "id_number": "1234 5678 9012",
    "confidence": 78.3
  },
  "signals": {
    "ocr_consistency": { "status": "PASS" },
    "image_integrity":  { "status": "PASS",    "ela_score": 12.4 },
    "tampering":        { "status": "WARNING",  "tampering_score": 28.1 },
    "metadata":         { "status": "WARNING",  "software": "Adobe Photoshop" },
    "qr":               { "status": "PASS",     "detected": true },
    "face_match":       { "status": "NOT_AVAILABLE" }
  },
  "reasons": [
    { "reason": "Post-processing software detected: Adobe Photoshop", "impact": -8 },
    { "reason": "Moderate ELA anomaly (28.1) detected", "impact": -8 }
  ],
  "processing_time": 2.14
}`}
        </pre>
      </div>

      <div className="card border border-amber-500/20 bg-amber-500/5">
        <div className="flex items-start gap-3">
          <Lock className="w-4 h-4 text-amber-400 mt-1 flex-shrink-0" />
          <div>
            <h4 className="text-white font-semibold text-sm mb-1">Security Notes</h4>
            <ul className="text-slate-400 text-sm space-y-1 list-disc list-inside">
              <li>Uploaded files are processed in temp directories and deleted after analysis</li>
              <li>Raw document text is not logged to disk</li>
              <li>File type and size validation enforced (max 10MB)</li>
              <li>CORS restricted to localhost origins in this MVP</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
