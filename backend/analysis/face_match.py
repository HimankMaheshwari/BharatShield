"""
Face Match Module — Optional identity verification.
Returns NOT_AVAILABLE if no selfie is provided.
For MVP: stub that gracefully handles missing selfie.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def match_faces(document_path: str, selfie_path: Optional[str]) -> Dict[str, Any]:
    """
    Compare document photo with selfie.
    Returns NOT_AVAILABLE if selfie not provided.
    """
    if not selfie_path:
        return {
            "status": "NOT_AVAILABLE",
            "similarity": None,
            "confidence": None,
            "details": "No selfie provided — identity match not performed.",
        }

    # Try basic OpenCV face detection as a lightweight check
    try:
        import cv2
        import numpy as np

        doc_img = cv2.imread(document_path)
        selfie_img = cv2.imread(selfie_path)

        if doc_img is None or selfie_img is None:
            return {
                "status": "NOT_AVAILABLE",
                "similarity": None,
                "confidence": None,
                "details": "Could not load images for face comparison.",
            }

        # Use Haar cascade for face detection only (no matching)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        doc_gray = cv2.cvtColor(doc_img, cv2.COLOR_BGR2GRAY)
        selfie_gray = cv2.cvtColor(selfie_img, cv2.COLOR_BGR2GRAY)

        doc_faces = face_cascade.detectMultiScale(doc_gray, 1.1, 4)
        selfie_faces = face_cascade.detectMultiScale(selfie_gray, 1.1, 4)

        doc_face_found = len(doc_faces) > 0
        selfie_face_found = len(selfie_faces) > 0

        if not doc_face_found:
            return {
                "status": "NOT_AVAILABLE",
                "similarity": None,
                "confidence": None,
                "details": "No face detected in document image.",
            }

        if not selfie_face_found:
            return {
                "status": "NOT_AVAILABLE",
                "similarity": None,
                "confidence": None,
                "details": "No face detected in selfie.",
            }

        # Without a proper embedding model, we can't reliably compare
        # Return NOT_AVAILABLE rather than a fake score
        return {
            "status": "NOT_AVAILABLE",
            "similarity": None,
            "confidence": None,
            "details": "Faces detected in both images, but reliable face matching requires a face embedding model not included in this MVP.",
        }

    except Exception as e:
        logger.warning(f"Face match error: {e}")
        return {
            "status": "NOT_AVAILABLE",
            "similarity": None,
            "confidence": None,
            "details": "Face matching unavailable in this environment.",
        }
