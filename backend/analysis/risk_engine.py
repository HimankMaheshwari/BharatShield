"""
Risk Engine — Deterministic weighted scoring.

Every deduction is evidence-based and produces an explanation.
Score starts at 100 and calibrated deductions are applied based on forensic findings.
"""
from typing import Dict, Any, List


# --- Signal status constants ---
PASS = "PASS"
WARNING = "WARNING"
SUSPICIOUS = "SUSPICIOUS"
NOT_AVAILABLE = "NOT_AVAILABLE"


def _ocr_signal(ocr: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """
    Evaluate OCR consistency and text extraction confidence.
    Low-quality OCR reduces confidence rather than implying fraud.
    """
    reasons = []
    score_deduction = 0
    details_parts = []

    if not ocr.get("available", False):
        status = NOT_AVAILABLE
        details = ocr.get("error", "OCR text extraction unavailable")
        reasons.append({
            "reason": f"OCR text extraction unavailable — document text could not be verified",
            "impact": -15,
            "category": "OCR",
        })
        return (
            {
                "status": status,
                "score": 0,
                "confidence": 0.0,
                "document_type": "UNKNOWN",
                "details": details,
            },
            reasons,
        )
    else:
        confidence = ocr.get("confidence", 0.0)
        raw_text = ocr.get("raw_text", "")
        doc_type = ocr.get("document_type", "UNKNOWN")

        issues = 0

        # Very low OCR confidence (e.g. heavily degraded image)
        if confidence < 35 and len(raw_text) < 40:
            issues += 1
            score_deduction += 6
            reasons.append({
                "reason": f"Low OCR text clarity ({confidence:.0f}%) — text partially unreadable due to image blur or resolution",
                "impact": -6,
                "category": "OCR",
            })
            details_parts.append(f"Low text clarity ({confidence:.0f}%)")

        elif confidence < 60:
            issues += 1
            score_deduction += 3
            reasons.append({
                "reason": f"OCR confidence moderate ({confidence:.0f}%) — some text fields may need manual review",
                "impact": -3,
                "category": "OCR",
            })

        # Missing key fields due to image quality
        missing_fields = []
        if not ocr.get("name"):
            missing_fields.append("name")
        if not ocr.get("id_number"):
            missing_fields.append("ID number")
        if not ocr.get("dob"):
            missing_fields.append("date of birth")

        if len(missing_fields) >= 3:
            issues += 1
            score_deduction += 5
            reasons.append({
                "reason": f"Could not extract standard fields ({', '.join(missing_fields)}) — document image may be low resolution",
                "impact": -5,
                "category": "OCR",
            })
        elif len(missing_fields) == 2:
            score_deduction += 3
            reasons.append({
                "reason": f"Some fields unextracted ({', '.join(missing_fields)})",
                "impact": -3,
                "category": "OCR",
            })

        # Unknown document type
        if doc_type == "UNKNOWN":
            issues += 1
            score_deduction += 4
            reasons.append({
                "reason": "Document type not recognized from text patterns",
                "impact": -4,
                "category": "OCR",
            })

        if issues == 0 and score_deduction == 0:
            status = PASS
            details = f"OCR confidence {confidence:.0f}% — document type and key fields extracted"
            reasons.append({
                "reason": f"OCR extraction verified ({doc_type}) with {confidence:.0f}% confidence",
                "impact": 0,
                "category": "OCR",
            })
        elif issues <= 1 and score_deduction <= 6:
            status = WARNING
            details = "; ".join(details_parts) if details_parts else "Moderate OCR confidence"
        else:
            status = WARNING  # Low quality OCR is a quality issue, not automatic fraud
            details = "OCR extracted partial text with low confidence"

        signal_score = max(0, 100 - score_deduction * 4)

    return (
        {
            "status": status,
            "score": signal_score,
            "confidence": ocr.get("confidence", 0),
            "document_type": ocr.get("document_type", "UNKNOWN"),
            "details": details if "details" in dir() else "",
        },
        reasons,
    )


def _image_integrity_signal(forensics: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """
    Evaluate image integrity (resolution, aspect ratio, overall quality).
    Separates natural compression/quality from tampering.
    """
    reasons = []
    dimensions = forensics.get("dimensions", {})
    compression = forensics.get("compression", {})

    issues = 0
    score_deduction = 0

    # Dimension and resolution checks
    if dimensions.get("available") and dimensions.get("anomalies"):
        for anomaly in dimensions["anomalies"]:
            issues += 1
            score_deduction += 3
            reasons.append({
                "reason": f"Image quality note: {anomaly}",
                "impact": -3,
                "category": "IMAGE",
            })

    # Compression quality level
    if compression.get("available"):
        comp_score = compression.get("compression_score", 0.0)
        if comp_score >= 18:
            issues += 1
            score_deduction += 4
            for note in compression.get("notes", []):
                reasons.append({
                    "reason": note,
                    "impact": -4,
                    "category": "IMAGE",
                })
        elif comp_score >= 8:
            # Minor compression — informational
            for note in compression.get("notes", []):
                reasons.append({
                    "reason": note,
                    "impact": 0,
                    "category": "IMAGE",
                })

    if issues == 0:
        status = PASS
        reasons.append({
            "reason": "Image resolution, dimensions, and visual integrity normal",
            "impact": 0,
            "category": "IMAGE",
        })
        details = "Image resolution and structure are intact"
    elif issues == 1:
        status = WARNING
        details = "Image shows compression artifacts or lower resolution"
    else:
        status = WARNING
        details = "Image quality is noticeably compressed or low resolution"

    return (
        {
            "status": status,
            "score": max(0, 100 - score_deduction * 4),
            "details": details,
        },
        reasons,
    )


def _tampering_signal(forensics: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """
    Evaluate evidence of digital splicing, patch editing, or localized tampering.
    """
    reasons = []
    ela = forensics.get("ela", {})
    edge = forensics.get("edge", {})
    tampering_score = forensics.get("tampering_score", 0.0)
    suspicious_regions = forensics.get("suspicious_regions", [])

    issues = 0
    score_deduction = 0

    # Localized ELA anomaly regions
    if suspicious_regions:
        issues += 2
        ded = 18 if len(suspicious_regions) == 1 else 25
        score_deduction += ded
        reasons.append({
            "reason": f"Localized compression inconsistency detected in {len(suspicious_regions)} region(s): {', '.join(suspicious_regions[:3])} — indicates possible digital splicing/patching",
            "impact": -ded,
            "category": "TAMPERING",
        })

    # Edge splicing anomalies
    if edge.get("available") and edge.get("edge_score", 0) > 35:
        issues += 1
        score_deduction += 8
        reasons.append({
            "reason": f"Edge gradient discontinuity detected (score={edge['edge_score']:.1f}) — suggests sharp digital insertion border",
            "impact": -8,
            "category": "TAMPERING",
        })

    # Composite tampering evaluation
    if tampering_score >= 35 and not suspicious_regions:
        issues += 1
        score_deduction += 8
        reasons.append({
            "reason": f"Composite forensic tampering indicator elevated ({tampering_score:.1f}/100)",
            "impact": -8,
            "category": "TAMPERING",
        })

    if issues == 0:
        status = PASS
        reasons.append({
            "reason": "No localized digital splicing or tampering artifacts detected",
            "impact": 0,
            "category": "TAMPERING",
        })
        details = "No localized tampering indicators found"
    elif issues == 1:
        status = WARNING
        details = f"Minor localized forensic irregularities (score {tampering_score:.1f}/100)"
    else:
        status = SUSPICIOUS
        details = f"Localized splicing / compression anomalies detected ({len(suspicious_regions)} region(s))"

    return (
        {
            "status": status,
            "score": max(0, 100 - score_deduction * 4),
            "tampering_score": tampering_score,
            "suspicious_regions": suspicious_regions,
            "details": details,
        },
        reasons,
    )


def _metadata_signal(metadata: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """Evaluate metadata anomalies."""
    reasons = []
    issues = 0
    score_deduction = 0

    if not metadata.get("available", False):
        return (
            {
                "status": NOT_AVAILABLE,
                "score": 0,
                "software": None,
                "anomalies": [],
                "details": metadata.get("error", "Metadata unavailable."),
            },
            reasons,
        )

    anomalies = metadata.get("anomalies", [])

    for anomaly in anomalies:
        anomaly_lower = anomaly.lower()
        if "editing software" in anomaly_lower or "photoshop" in anomaly_lower or "gimp" in anomaly_lower:
            issues += 1
            score_deduction += 8
            reasons.append({
                "reason": f"Post-processing software detected in metadata: {metadata.get('software', 'unknown')}",
                "impact": -8,
                "category": "METADATA",
            })
        elif "future" in anomaly_lower or "unusually old" in anomaly_lower:
            issues += 1
            score_deduction += 6
            reasons.append({
                "reason": f"Suspicious EXIF timestamp: {anomaly}",
                "impact": -6,
                "category": "METADATA",
            })
        elif "no exif" in anomaly_lower or "stripped" in anomaly_lower:
            # Common on web uploads / screenshots — informational only
            reasons.append({
                "reason": "No EXIF metadata (standard for web uploads or screenshots)",
                "impact": 0,
                "category": "METADATA",
            })

    if issues == 0:
        status = PASS
        reasons.append({
            "reason": "No suspicious metadata or editing software tags detected",
            "impact": 0,
            "category": "METADATA",
        })
        details = "Metadata appears normal"
    elif issues == 1:
        status = WARNING
        details = f"{len(anomalies)} metadata flag(s) detected"
    else:
        status = SUSPICIOUS
        details = "Multiple metadata anomalies detected"

    return (
        {
            "status": status,
            "score": max(0, 100 - score_deduction * 4),
            "software": metadata.get("software"),
            "creation_time": metadata.get("creation_time"),
            "anomalies": anomalies,
            "details": details,
        },
        reasons,
    )


def _qr_signal(qr: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """Evaluate QR code findings."""
    reasons = []

    if not qr.get("available", False):
        return (
            {"status": NOT_AVAILABLE, "score": 0, "detected": False, "details": "QR detection unavailable"},
            reasons,
        )

    detected = qr.get("detected", False)
    decoded_data = qr.get("decoded_data")
    structure_status = qr.get("structure_status", "NOT_DETECTED")

    if not detected:
        return (
            {
                "status": NOT_AVAILABLE,
                "score": 100,
                "detected": False,
                "decoded_data": None,
                "details": "No QR code detected — document may not include one.",
            },
            reasons,
        )

    if structure_status == "DETECTED_NOT_DECODED":
        reasons.append({
            "reason": "QR code detected but could not be decoded — may be low resolution or non-standard encoding",
            "impact": -3,
            "category": "QR",
        })
        status = WARNING
    elif structure_status == "DECODED":
        reasons.append({
            "reason": "QR code successfully decoded",
            "impact": 0,
            "category": "QR",
        })
        status = PASS
    else:
        status = NOT_AVAILABLE

    return (
        {
            "status": status,
            "score": 100 if status == PASS else 85,
            "detected": detected,
            "decoded_data": decoded_data,
            "structure_status": structure_status,
            "details": qr.get("details", ""),
        },
        reasons,
    )


def _face_signal(face: Dict[str, Any]) -> tuple[Dict, List[Dict]]:
    """Evaluate face match result."""
    status = face.get("status", NOT_AVAILABLE)
    return (
        {
            "status": status,
            "score": 0 if status == NOT_AVAILABLE else (100 if status == PASS else 50),
            "similarity": face.get("similarity"),
            "confidence": face.get("confidence"),
            "details": face.get("details", "Identity match not performed."),
        },
        [],
    )


def compute_risk_score(
    ocr: Dict[str, Any],
    forensics: Dict[str, Any],
    metadata: Dict[str, Any],
    qr: Dict[str, Any],
    face: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Deterministic weighted risk scoring engine.
    Calibrated to separate image quality issues from tampering evidence.
    """
    score = 100
    all_reasons = []

    # --- Evaluate each signal ---
    ocr_signal, ocr_reasons = _ocr_signal(ocr)
    integrity_signal, integrity_reasons = _image_integrity_signal(forensics)
    tampering_signal, tampering_reasons = _tampering_signal(forensics)
    metadata_signal, metadata_reasons = _metadata_signal(metadata)
    qr_signal, qr_reasons = _qr_signal(qr)
    face_signal, face_reasons = _face_signal(face)

    all_reasons.extend(ocr_reasons)
    all_reasons.extend(integrity_reasons)
    all_reasons.extend(tampering_reasons)
    all_reasons.extend(metadata_reasons)
    all_reasons.extend(qr_reasons)
    all_reasons.extend(face_reasons)

    # Apply deductions from non-zero reasons
    for reason in all_reasons:
        impact = reason.get("impact", 0)
        if impact < 0:
            score += impact

    score = max(0, min(100, score))

    # --- Risk Level ---
    if score >= 80:
        risk_level = "LOW"
    elif score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Display reasons
    display_reasons = [r for r in all_reasons if r["impact"] != 0]
    if not display_reasons:
        display_reasons = [r for r in all_reasons if r["impact"] == 0][:3]

    return {
        "trust_score": int(score),
        "risk_level": risk_level,
        "signals": {
            "ocr_consistency": ocr_signal,
            "image_integrity": integrity_signal,
            "tampering": tampering_signal,
            "metadata": metadata_signal,
            "qr": qr_signal,
            "face_match": face_signal,
        },
        "reasons": display_reasons,
        "all_reasons": all_reasons,
    }
