"""
QR Code Detection Module
Detects and decodes QR codes using OpenCV's built-in QR detector.
Falls back to pyzbar if available.
"""
import logging
from typing import Dict, Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available — QR detection skipped")

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


def detect_qr(image_path: str) -> Dict[str, Any]:
    """
    Detect and decode QR codes in a document image.
    Uses OpenCV first, then pyzbar as fallback.
    """
    if not CV2_AVAILABLE:
        return {
            "available": False,
            "detected": False,
            "decoded_data": None,
            "count": 0,
            "structure_status": "NOT_AVAILABLE",
            "details": "OpenCV not installed",
        }

    try:
        img = cv2.imread(image_path)
        if img is None:
            return {
                "available": True,
                "detected": False,
                "decoded_data": None,
                "count": 0,
                "structure_status": "NOT_AVAILABLE",
                "details": "Could not read image",
            }

        # --- Method 1: OpenCV QR Detector ---
        qr_detector = cv2.QRCodeDetector()
        decoded_text, points, _ = qr_detector.detectAndDecode(img)

        decoded_data = None
        count = 0
        method = "opencv"

        if decoded_text:
            decoded_data = decoded_text.strip()
            count = 1
        elif points is not None:
            # Detected but not decoded
            count = 1

        # --- Method 2: pyzbar fallback ---
        if not decoded_data and PYZBAR_AVAILABLE:
            try:
                from PIL import Image
                pil_img = Image.open(image_path)
                barcodes = pyzbar.decode(pil_img)
                for barcode in barcodes:
                    if barcode.type in ("QRCODE",):
                        decoded_data = barcode.data.decode("utf-8", errors="replace")
                        count += 1
                        method = "pyzbar"
            except Exception as e:
                logger.debug(f"pyzbar failed: {e}")

        # Structure analysis for decoded QR
        structure_status = "NOT_DETECTED"
        qr_details = "No QR code detected."

        if count > 0 and decoded_data:
            structure_status = "DECODED"
            qr_details = f"QR code decoded via {method}. Data length: {len(decoded_data)} chars."

            # Basic validation: Aadhaar QR typically starts with specific format
            if decoded_data.startswith("http"):
                qr_details += " Contains URL reference."
            elif decoded_data.isdigit():
                qr_details += " QR contains numeric data."

        elif count > 0:
            structure_status = "DETECTED_NOT_DECODED"
            qr_details = "QR code detected but could not be decoded — may be damaged or encrypted."

        return {
            "available": True,
            "detected": count > 0,
            "decoded_data": decoded_data[:500] if decoded_data else None,  # Truncate for safety
            "count": count,
            "structure_status": structure_status,
            "details": qr_details,
        }

    except Exception as e:
        logger.error(f"QR detection failed: {e}")
        return {
            "available": True,
            "detected": False,
            "decoded_data": None,
            "count": 0,
            "structure_status": "ERROR",
            "details": f"QR detection error: {str(e)}",
        }
