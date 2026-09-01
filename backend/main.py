"""
BharatShield Backend — FastAPI Main Application
"""
import os
import uuid
import time
import shutil
import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from models import VerificationResponse
from database import init_db, save_verification, get_all_verifications
from analysis.ocr import extract_ocr
from analysis.forensics import analyze_forensics
from analysis.metadata_extractor import extract_metadata
from analysis.qr_detector import detect_qr
from analysis.face_match import match_faces
from analysis.risk_engine import compute_risk_score

app = FastAPI(
    title="BharatShield API",
    description="AI-Powered Document Fraud Detection",
    version="1.0.0",
)

# Allowed origins for CORS (local dev, Vercel deployments, Render, and env overrides)
env_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
origins = list(set(DEFAULT_ORIGINS + env_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Allowed file types
ALLOWED_TYPES = {
    "image/png", "image/jpeg", "image/jpg", "image/webp",
    "application/pdf",
}
MAX_FILE_SIZE_MB = 10

TEMP_DIR = Path(__file__).parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Serve demo test documents
app.mount("/demo", StaticFiles(directory=str(TEST_DATA_DIR)), name="demo")

@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BharatShield"}


@app.post("/api/verify")
async def verify_document(
    document: UploadFile = File(...),
    selfie: Optional[UploadFile] = File(None),
):
    start_time = time.time()
    verification_id = str(uuid.uuid4())[:8].upper()

    # --- File validation ---
    if document.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {document.content_type}. Accepted: PNG, JPG, WEBP, PDF",
        )

    content = await document.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.",
        )

    # Save to temp directory
    suffix = Path(document.filename or "doc.jpg").suffix or ".jpg"
    tmp_path = TEMP_DIR / f"{verification_id}{suffix}"
    with open(tmp_path, "wb") as f:
        f.write(content)

    selfie_path = None
    if selfie and selfie.content_type in ALLOWED_TYPES:
        selfie_content = await selfie.read()
        selfie_suffix = Path(selfie.filename or "selfie.jpg").suffix or ".jpg"
        selfie_path = TEMP_DIR / f"{verification_id}_selfie{selfie_suffix}"
        with open(selfie_path, "wb") as f:
            f.write(selfie_content)

    try:
        # --- Run analysis pipeline ---
        ocr_result = extract_ocr(str(tmp_path))
        forensics_result = analyze_forensics(str(tmp_path))
        metadata_result = extract_metadata(str(tmp_path))
        qr_result = detect_qr(str(tmp_path))
        face_result = match_faces(str(tmp_path), str(selfie_path) if selfie_path else None)

        # --- Risk Engine ---
        risk_output = compute_risk_score(
            ocr=ocr_result,
            forensics=forensics_result,
            metadata=metadata_result,
            qr=qr_result,
            face=face_result,
        )

        processing_time = round(time.time() - start_time, 2)

        response = {
            "verification_id": verification_id,
            "document_type": ocr_result.get("document_type", "UNKNOWN"),
            "trust_score": risk_output["trust_score"],
            "risk_level": risk_output["risk_level"],
            "ocr": ocr_result,
            "signals": {
                "ocr_consistency": risk_output["signals"]["ocr_consistency"],
                "image_integrity": risk_output["signals"]["image_integrity"],
                "tampering": risk_output["signals"]["tampering"],
                "metadata": risk_output["signals"]["metadata"],
                "qr": risk_output["signals"]["qr"],
                "face_match": risk_output["signals"]["face_match"],
            },
            "reasons": risk_output["reasons"],
            "processing_time": processing_time,
        }

        # Save to history
        await save_verification(
            verification_id=verification_id,
            document_type=response["document_type"],
            trust_score=response["trust_score"],
            risk_level=response["risk_level"],
            filename=document.filename or "unknown",
        )

        return JSONResponse(content=response)

    finally:
        # Cleanup temp files
        try:
            if tmp_path.exists():
                tmp_path.unlink()
            if selfie_path and selfie_path.exists():
                selfie_path.unlink()
        except Exception:
            pass


@app.get("/api/history")
async def get_history():
    records = await get_all_verifications()
    return {"history": records, "total": len(records)}


@app.get("/api/demo-docs")
async def list_demo_docs():
    """List available demo test documents."""
    test_data_dir = Path(__file__).parent / "test_data"
    docs = []
    if test_data_dir.exists():
        for f in test_data_dir.iterdir():
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                docs.append({"name": f.name, "path": str(f)})
    return {"docs": docs}
