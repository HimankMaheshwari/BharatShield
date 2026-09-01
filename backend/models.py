"""
Pydantic models for BharatShield API responses.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SignalResult(BaseModel):
    status: str  # PASS | WARNING | SUSPICIOUS | NOT_AVAILABLE
    score: float = 0
    details: Optional[str] = None


class OCRResult(BaseModel):
    available: bool
    raw_text: Optional[str] = None
    document_type: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0
    error: Optional[str] = None


class ReasonItem(BaseModel):
    reason: str
    impact: int
    category: Optional[str] = None


class SignalsResult(BaseModel):
    ocr_consistency: Optional[Dict[str, Any]] = None
    image_integrity: Optional[Dict[str, Any]] = None
    tampering: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    qr: Optional[Dict[str, Any]] = None
    face_match: Optional[Dict[str, Any]] = None


class VerificationResponse(BaseModel):
    verification_id: str
    document_type: str
    trust_score: int
    risk_level: str
    ocr: Optional[Dict[str, Any]] = None
    signals: Optional[SignalsResult] = None
    reasons: Optional[List[Dict[str, Any]]] = None
    processing_time: float
