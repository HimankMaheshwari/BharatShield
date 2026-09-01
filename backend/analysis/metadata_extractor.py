"""
Metadata Extraction Module
Extracts EXIF and file metadata using Pillow.
"""
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Known editing software keywords — presence is a risk signal, not conclusive
EDITING_SOFTWARE_KEYWORDS = [
    "adobe", "photoshop", "gimp", "paint", "affinity",
    "snapseed", "lightroom", "illustrator", "inkscape",
    "canva", "picsart", "fotor", "pixlr",
]


def extract_metadata(image_path: str) -> Dict[str, Any]:
    """
    Extract image metadata (EXIF, ICC, etc.) and flag anomalies.
    Returns metadata dict with detected anomalies.
    """
    if not PIL_AVAILABLE:
        return {
            "available": False,
            "anomalies": [],
            "software": None,
            "creation_time": None,
            "modification_time": None,
            "camera_make": None,
            "camera_model": None,
            "raw_exif": {},
            "error": "Pillow not installed",
        }

    try:
        img = Image.open(image_path)
        exif_data = {}
        anomalies: List[str] = []
        software = None
        creation_time = None
        camera_make = None
        camera_model = None

        # --- EXIF extraction ---
        raw_exif = img._getexif() if hasattr(img, "_getexif") else None
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag = TAGS.get(tag_id, tag_id)
                # Only include string/int values for safety
                if isinstance(value, (str, int, float)):
                    exif_data[str(tag)] = str(value)[:200]

            software = exif_data.get("Software", None)
            creation_time = exif_data.get("DateTime", exif_data.get("DateTimeOriginal", None))
            camera_make = exif_data.get("Make", None)
            camera_model = exif_data.get("Model", None)

        # --- Check file modification time ---
        stat = Path(image_path).stat()
        file_mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # --- Anomaly detection ---

        # 1. Editing software present
        if software:
            sw_lower = software.lower()
            for kw in EDITING_SOFTWARE_KEYWORDS:
                if kw in sw_lower:
                    anomalies.append(
                        f"Editing software detected in metadata: '{software}'"
                    )
                    break

        # 2. No camera info but file claims to be a photo
        if not camera_make and not camera_model:
            if Path(image_path).suffix.lower() in {".jpg", ".jpeg"}:
                # JPEG without camera info can be screenshot or edited
                anomalies.append("No camera information in EXIF — may be screenshot or edited")

        # 3. EXIF date mismatch
        if creation_time:
            try:
                # Parse EXIF datetime format: "2023:01:15 12:34:56"
                exif_dt = datetime.strptime(creation_time, "%Y:%m:%d %H:%M:%S")
                # If creation is far in future = suspicious
                if exif_dt > datetime.now():
                    anomalies.append(f"EXIF creation date is in the future: {creation_time}")
                elif exif_dt.year < 2000:
                    anomalies.append(f"Unusually old EXIF date: {creation_time}")
            except Exception:
                pass  # Non-standard date format — don't flag

        # 4. Missing EXIF entirely for a JPEG
        if not raw_exif and Path(image_path).suffix.lower() in {".jpg", ".jpeg"}:
            anomalies.append("JPEG has no EXIF data — stripped metadata is a possible indicator")

        return {
            "available": True,
            "software": software,
            "creation_time": creation_time,
            "file_mtime": file_mtime,
            "camera_make": camera_make,
            "camera_model": camera_model,
            "raw_exif": exif_data,
            "anomalies": anomalies,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Metadata extraction failed: {e}")
        return {
            "available": False,
            "anomalies": [],
            "software": None,
            "creation_time": None,
            "camera_make": None,
            "camera_model": None,
            "raw_exif": {},
            "error": str(e),
        }
