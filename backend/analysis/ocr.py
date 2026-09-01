"""
OCR Module — Extract text from documents using Tesseract or RapidOCR.
Auto-detects Tesseract binary on Windows and falls back to RapidOCR.
"""
import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# --- Engine Detection ---
TESSERACT_AVAILABLE = False
RAPIDOCR_AVAILABLE = False

# 1. Check Tesseract in standard Windows paths & PATH
TESSERACT_SEARCH_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\himan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    r"C:\Users\himan\AppData\Local\Tesseract-OCR\tesseract.exe",
    r"C:\Tesseract-OCR\tesseract.exe",
    r"C:\tools\tesseract\tesseract.exe",
]

try:
    import pytesseract
    from PIL import Image

    tess_path = shutil.which("tesseract")
    if not tess_path:
        for p in TESSERACT_SEARCH_PATHS:
            if os.path.exists(p):
                tess_path = p
                pytesseract.pytesseract.tesseract_cmd = p
                break

    if tess_path:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        logger.info(f"Tesseract OCR available at {tess_path}")
except Exception as e:
    logger.debug(f"Tesseract binary not available: {e}")

# 2. Check RapidOCR as local high-accuracy engine
rapid_engine = None
try:
    from rapidocr_onnxruntime import RapidOCR
    rapid_engine = RapidOCR()
    RAPIDOCR_AVAILABLE = True
    logger.info("RapidOCR (ONNX) engine initialized successfully")
except Exception as e:
    logger.debug(f"RapidOCR not available: {e}")


def _load_image(path: str):
    """Load image, converting PDF first page if needed."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        try:
            import pdf2image
            pages = pdf2image.convert_from_path(path, first_page=1, last_page=1)
            return pages[0] if pages else None
        except Exception as e:
            logger.warning(f"PDF load failed: {e}")
            return None
    else:
        try:
            from PIL import Image
            return Image.open(path).convert("RGB")
        except Exception as e:
            logger.error(f"Image load failed: {e}")
            return None


# --- Document classification patterns ---
DOCUMENT_PATTERNS = {
    "PAN": [
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        r"income\s*tax",
        r"permanent\s*account",
        r"pan\s*card",
        r"\bpan\b",
    ],
    "AADHAAR": [
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        r"aadhaar|aadhar|uidai|unique\s*identification",
        r"government\s*of\s*india",
        r"enrolment\s*no",
    ],
    "PASSPORT": [
        r"\bpassport\b",
        r"republic\s*of\s*india",
        r"\b[A-Z][0-9]{7}\b",
        r"nationality|place\s*of\s*birth",
    ],
    "DRIVING_LICENSE": [
        r"driving\s*licen[cs]e",
        r"transport\s*department",
        r"dl\s*no|licence\s*no",
        r"\b[A-Z]{2}\d{2}\s?\d{11}\b",
    ],
    "VOTER_ID": [
        r"election\s*commission",
        r"voter|electors",
        r"epic\s*no",
    ],
}


def classify_document(text: str) -> str:
    """Rule-based document classification from OCR text."""
    text_lower = text.lower()
    scores = {}
    for doc_type, patterns in DOCUMENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1
        scores[doc_type] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "UNKNOWN"
    return best


def _extract_name(text: str) -> Optional[str]:
    """Extract a name from OCR text (Title Case or UPPERCASE)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # 1. Check if line is "Name:" and next line is the name
    for i, line in enumerate(lines):
        if re.match(r"^Name[:\s]*$", line, re.IGNORECASE) and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r"^[A-Za-z]+(?:\s+[A-Za-z]+)*$", next_line):
                return next_line
        m = re.match(r"^Name[:\s]+([A-Za-z]+(?:\s+[A-Za-z]+)*)$", line, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val.upper() not in {"INCOME TAX DEPARTMENT", "GOVERNMENT OF INDIA", "PERMANENT ACCOUNT NUMBER"}:
                return val

    # 2. Heuristic: look for 2-3 capitalized words on a single line
    for line in lines:
        clean = line.strip()
        if re.match(r"^[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,2}$", clean):
            if clean.upper() not in {
                "INCOME TAX DEPARTMENT", "GOVERNMENT OF INDIA", "PERMANENT ACCOUNT NUMBER",
                "BHARATSHIELD TEST FIXTURE", "DEMO ONLY", "NOT A REAL DOCUMENT", "FATHER'S NAME", "DATE OF BIRTH"
            }:
                return clean
    return None


def _extract_dob(text: str) -> Optional[str]:
    """Extract date of birth."""
    patterns = [
        r"(?:dob|d\.o\.b|date\s*of\s*birth|born)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_id_number(text: str, doc_type: str) -> Optional[str]:
    """Extract document-specific ID number."""
    if doc_type == "PAN" or re.search(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text):
        m = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", text)
        if m:
            return m.group(1)
    if doc_type == "AADHAAR":
        # 1. 4-4-4 spaced digits
        m = re.search(r"\b(\d{4}\s\d{4}\s\d{4})\b", text)
        if m:
            return m.group(1)
        # 2. Continuous 12 digits
        m_cont = re.search(r"\b([1-9]\d{11})\b", text)
        if m_cont:
            d = m_cont.group(1)
            return f"{d[:4]} {d[4:8]} {d[8:]}"
        # 3. Match 12 digits anywhere in a line (excluding lines with dates)
        for line in text.split("\n"):
            if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", line):
                continue
            digits = re.sub(r"\D", "", line)
            if len(digits) >= 12:
                d = digits[-12:]
                return f"{d[:4]} {d[4:8]} {d[8:]}"
    if doc_type == "PASSPORT":
        m = re.search(r"\b([A-Z][0-9]{7})\b", text)
        if m:
            return m.group(1)
    # Generic
    m = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z]|\d{4}\s\d{4}\s\d{4}|[A-Z][0-9]{7})\b", text)
    if m:
        return m.group(1)
    return None


def _extract_address(text: str) -> Optional[str]:
    """Extract address block."""
    patterns = [
        r"(?:address|addr|s/o|w/o|d/o)[:\s]+(.+?)(?:\n\n|\Z)",
        r"(?:house|flat|village|dist|pin|sector|road|nagar)[^\n]*\n(?:[^\n]+\n){0,3}",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.DOTALL)
        if m:
            addr = m.group(0).strip()
            return addr[:200] if len(addr) > 200 else addr
    return None


def extract_ocr(image_path: str) -> Dict[str, Any]:
    """
    Main OCR extraction function.
    Uses Tesseract if available, otherwise uses RapidOCR (ONNX).
    """
    # Strategy 1: Tesseract
    if TESSERACT_AVAILABLE:
        try:
            img = _load_image(image_path)
            if img is not None:
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                confidences = [int(c) for c in data["conf"] if int(c) > 0]
                avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
                raw_text = pytesseract.image_to_string(img, config="--psm 6")
                if raw_text.strip():
                    doc_type = classify_document(raw_text)
                    return {
                        "available": True,
                        "engine": "Tesseract",
                        "raw_text": raw_text[:2000],
                        "document_type": doc_type,
                        "name": _extract_name(raw_text),
                        "dob": _extract_dob(raw_text),
                        "id_number": _extract_id_number(raw_text, doc_type),
                        "address": _extract_address(raw_text),
                        "confidence": round(avg_conf, 1),
                        "error": None,
                    }
        except Exception as e:
            logger.warning(f"Tesseract extraction failed: {e}")

    # Strategy 2: RapidOCR
    if RAPIDOCR_AVAILABLE and rapid_engine is not None:
        try:
            results, _ = rapid_engine(image_path)
            if results:
                lines = [r[1] for r in results if r[1]]
                confs = [float(r[2]) * 100 for r in results if len(r) > 2 and r[2] is not None]
                avg_conf = sum(confs) / len(confs) if confs else 0.0
                raw_text = "\n".join(lines)
                doc_type = classify_document(raw_text)

                return {
                    "available": True,
                    "engine": "RapidOCR",
                    "raw_text": raw_text[:2000],
                    "document_type": doc_type,
                    "name": _extract_name(raw_text),
                    "dob": _extract_dob(raw_text),
                    "id_number": _extract_id_number(raw_text, doc_type),
                    "address": _extract_address(raw_text),
                    "confidence": round(avg_conf, 1),
                    "error": None,
                }
        except Exception as e:
            logger.error(f"RapidOCR extraction failed: {e}")

    # Fallback when no OCR engine succeeded
    return {
        "available": False,
        "raw_text": "",
        "document_type": "UNKNOWN",
        "name": None,
        "dob": None,
        "id_number": None,
        "address": None,
        "confidence": 0.0,
        "error": "OCR engine not available",
    }
