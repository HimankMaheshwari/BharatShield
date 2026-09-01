"""
Image Forensics Module
Performs ELA (Error Level Analysis), edge analysis, and compression analysis
to detect potential image tampering.
"""
import io
import logging
import math
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not available — forensics degraded")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available — some forensics skipped")


def _ela_analysis(image_path: str, quality: int = 90) -> Dict[str, Any]:
    """
    Error Level Analysis (ELA).

    Re-saves image at known quality, then measures pixel difference.
    Detects localized differential compression (splicing/patching)
    without penalizing uniform compression across genuine documents.
    """
    if not PIL_AVAILABLE:
        return {"available": False, "ela_score": 0.0, "details": "Pillow not installed"}

    try:
        img = Image.open(image_path).convert("RGB")

        # Re-compress to JPEG at known quality
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert("RGB")

        # Compute absolute pixel difference (0 to 255)
        diff = ImageChops.difference(img, recompressed)
        diff_array = np.array(diff, dtype=np.float32)

        mean_ela = float(np.mean(diff_array))
        std_ela = float(np.std(diff_array))
        max_ela = float(np.max(diff_array))

        # Regional analysis — divide image into 3x3 grid
        h, w = diff_array.shape[:2]
        cell_h, cell_w = max(1, h // 3), max(1, w // 3)
        region_means = []
        for row in range(3):
            for col in range(3):
                y1, y2 = row * cell_h, min(h, (row + 1) * cell_h)
                x1, x2 = col * cell_w, min(w, (col + 1) * cell_w)
                cell = diff_array[y1:y2, x1:x2]
                region_means.append(float(np.mean(cell)) if cell.size > 0 else 0.0)

        overall_mean = sum(region_means) / len(region_means) if region_means else 0.0
        region_variance = sum((r - overall_mean) ** 2 for r in region_means) / len(region_means) if region_means else 0.0
        region_std = math.sqrt(region_variance)

        # Suspicious localized regions:
        # Flag ONLY when a region significantly deviates from the image-wide baseline
        suspicious_regions = []
        if overall_mean > 0.1 and region_std > 0.05:
            for i, r_mean in enumerate(region_means):
                z_score = (r_mean - overall_mean) / (region_std + 1e-6)
                ratio = r_mean / (overall_mean + 1e-6)
                if z_score > 2.0 and ratio > 2.4 and (r_mean - overall_mean) > 0.4:
                    row = i // 3
                    col = i % 3
                    suspicious_regions.append(f"Region [{row},{col}]")

        # ela_score measures localized splicing anomaly (0-100)
        # Uniform compression (even low quality) gives low ela_score
        ela_score = min(100.0, len(suspicious_regions) * 50.0)

        return {
            "available": True,
            "ela_score": round(ela_score, 2),
            "mean_ela": round(mean_ela, 2),
            "std_ela": round(std_ela, 2),
            "max_ela": round(max_ela, 2),
            "region_variance": round(region_variance, 2),
            "suspicious_regions": suspicious_regions,
            "details": f"ELA mean={mean_ela:.1f}, anomalies={len(suspicious_regions)}",
        }
    except Exception as e:
        logger.error(f"ELA failed: {e}")
        return {"available": False, "ela_score": 0.0, "details": f"ELA error: {e}"}


def _edge_analysis(image_path: str) -> Dict[str, Any]:
    """
    Detects unnatural sharp boundary inserts or digital paste borders.
    Calibrated so standard document text layouts are not flagged as tampering.
    """
    if not CV2_AVAILABLE:
        return {"available": False, "edge_score": 0.0, "details": "OpenCV not available"}

    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"available": False, "edge_score": 0.0, "details": "Could not read image"}

        # Laplacian for sharpness
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        lap_var = float(laplacian.var())

        # Canny edges
        edges = cv2.Canny(img, 50, 150)
        edge_density = float(np.sum(edges > 0)) / (img.shape[0] * img.shape[1])

        # Analyze sharpness consistency across blocks
        h, w = img.shape
        block_vars = []
        block_size = max(16, min(h, w) // 4)
        for r in range(0, h - block_size + 1, block_size):
            for c in range(0, w - block_size + 1, block_size):
                block = laplacian[r:r+block_size, c:c+block_size]
                block_vars.append(float(np.var(block)))

        # Compare maximum block sharpness to median block sharpness
        # Normal documents with text/photo/background have ratio ~3 to ~15
        # Splice inserts across flat background produce extreme ratio > 30
        if block_vars:
            median_var = float(np.median(block_vars)) + 1.0
            max_var = float(np.max(block_vars))
            discrepancy_ratio = max_var / median_var
            edge_score = min(100.0, max(0.0, (discrepancy_ratio - 25.0) * 3.0)) if discrepancy_ratio > 25.0 else 0.0
        else:
            edge_score = 0.0

        return {
            "available": True,
            "laplacian_variance": round(lap_var, 2),
            "edge_density": round(edge_density, 4),
            "edge_score": round(edge_score, 2),
            "details": f"Edge density={edge_density:.3f}, sharpness={lap_var:.1f}",
        }
    except Exception as e:
        logger.error(f"Edge analysis failed: {e}")
        return {"available": False, "edge_score": 0.0, "details": f"Edge error: {e}"}


def _compression_analysis(image_path: str) -> Dict[str, Any]:
    """
    Analyze JPEG compression artifacts and quality estimate.
    Identifies image quality level without falsely classifying it as tampering.
    """
    if not PIL_AVAILABLE:
        return {"available": False, "compression_score": 0.0}

    try:
        img = Image.open(image_path)
        format_info = {
            "format": img.format or "UNKNOWN",
            "mode": img.mode,
            "size": f"{img.size[0]}x{img.size[1]}",
        }

        jpeg_quality = None
        if hasattr(img, "quantization") and img.quantization:
            try:
                luma_dc = img.quantization[0][0]
                if luma_dc <= 2:
                    jpeg_quality = 95
                elif luma_dc <= 4:
                    jpeg_quality = 85
                elif luma_dc <= 8:
                    jpeg_quality = 75
                elif luma_dc <= 16:
                    jpeg_quality = 50
                else:
                    jpeg_quality = 30
            except Exception:
                jpeg_quality = None

        compression_score = 0.0
        notes = []
        if jpeg_quality is not None and jpeg_quality < 45:
            compression_score = 20.0
            notes.append(f"Low image quality ({jpeg_quality}% estimated) — high compression artifacts")
        elif jpeg_quality is not None and jpeg_quality < 70:
            compression_score = 8.0
            notes.append(f"Standard compression ({jpeg_quality}% estimated)")

        return {
            "available": True,
            "jpeg_quality_estimate": jpeg_quality,
            "format_info": format_info,
            "compression_score": round(compression_score, 2),
            "notes": notes,
            "details": f"Format={format_info['format']}, Quality={jpeg_quality or 'N/A'}",
        }
    except Exception as e:
        logger.error(f"Compression analysis failed: {e}")
        return {"available": False, "compression_score": 0.0, "details": str(e)}


def _validate_dimensions(image_path: str) -> Dict[str, Any]:
    """Check image dimensions and aspect ratio for document plausibility."""
    if not PIL_AVAILABLE:
        return {"available": False}

    try:
        img = Image.open(image_path)
        w, h = img.size
        aspect = w / h if h > 0 else 0

        anomalies = []
        if w < 300 or h < 200:
            anomalies.append("Image resolution is low (may impact OCR clarity)")
        if aspect < 0.35 or aspect > 4.5:
            anomalies.append(f"Unusual aspect ratio ({aspect:.2f})")

        return {
            "available": True,
            "width": w,
            "height": h,
            "aspect_ratio": round(aspect, 2),
            "resolution_ok": w >= 300 and h >= 200,
            "anomalies": anomalies,
        }
    except Exception as e:
        return {"available": False, "details": str(e)}


def analyze_forensics(image_path: str) -> Dict[str, Any]:
    """
    Master forensic analysis function.
    Combines ELA, edge, compression, and dimension analysis.
    """
    ela = _ela_analysis(image_path)
    edge = _edge_analysis(image_path)
    compression = _compression_analysis(image_path)
    dimensions = _validate_dimensions(image_path)

    # Tampering score is driven by localized ELA splicing + sharp edge splicing
    tampering_score = 0.0
    if ela.get("available"):
        tampering_score += ela.get("ela_score", 0.0) * 0.75
    if edge.get("available"):
        tampering_score += edge.get("edge_score", 0.0) * 0.25

    tampering_score = min(100.0, tampering_score)

    return {
        "ela": ela,
        "edge": edge,
        "compression": compression,
        "dimensions": dimensions,
        "tampering_score": round(tampering_score, 2),
        "suspicious_regions": ela.get("suspicious_regions", []),
    }
