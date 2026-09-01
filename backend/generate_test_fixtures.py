"""
Generate synthetic demo test fixtures for BharatShield.

Produces:
  test_data/clean_pan.png     — clean synthetic PAN-style card (expect ~85+ score)
  test_data/tampered_aadhaar.png — card with deliberate JPEG re-compression artifacts (expect lower score)

These are CLEARLY LABELLED as synthetic DEMO documents.
They are NOT real government documents.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os
import random
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "test_data"
OUTPUT_DIR.mkdir(exist_ok=True)


def _get_font(size: int):
    """Try to get a font, fall back to default."""
    try:
        # Try common system fonts on Windows
        for font_path in [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
        ]:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def create_clean_pan():
    """
    Create a clean, consistent synthetic PAN-style card.
    No tampering — high trust score expected.
    """
    W, H = 856, 540
    img = Image.new("RGB", (W, H), color=(245, 232, 196))  # cream background

    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, W, 80], fill=(0, 51, 102))

    font_large = _get_font(28)
    font_med = _get_font(20)
    font_small = _get_font(16)
    font_tiny = _get_font(13)

    # Header text
    draw.text((20, 15), "INCOME TAX DEPARTMENT", fill="white", font=font_large)
    draw.text((20, 48), "Government of India", fill=(200, 200, 255), font=font_small)
    draw.text((W - 200, 25), "PERMANENT ACCOUNT NUMBER", fill="white", font=font_tiny)

    # Emblem placeholder (circle)
    draw.ellipse([W - 80, 5, W - 10, 75], outline="gold", width=3)
    draw.text((W - 60, 30), "GOI", fill="gold", font=font_tiny)

    # Photo box
    draw.rectangle([30, 110, 200, 290], fill=(220, 220, 220), outline=(100, 100, 100), width=2)
    draw.text((65, 185), "[PHOTO]", fill=(120, 120, 120), font=font_small)

    # PAN Number (bold, large)
    pan_number = "ABCDE1234F"
    draw.text((240, 100), "PAN", fill=(80, 80, 80), font=font_small)
    draw.text((240, 125), pan_number, fill=(10, 10, 10), font=_get_font(36))

    # Separator line
    draw.line([240, 175, W - 30, 175], fill=(150, 150, 150), width=1)

    # Name
    draw.text((240, 185), "Name", fill=(100, 100, 100), font=font_tiny)
    draw.text((240, 205), "RAJESH KUMAR SHARMA", fill=(10, 10, 10), font=font_med)

    # Father's name
    draw.text((240, 245), "Father's Name", fill=(100, 100, 100), font=font_tiny)
    draw.text((240, 265), "SURESH KUMAR SHARMA", fill=(10, 10, 10), font=font_med)

    # DOB
    draw.text((240, 305), "Date of Birth", fill=(100, 100, 100), font=font_tiny)
    draw.text((240, 325), "15/08/1985", fill=(10, 10, 10), font=font_med)

    # Signature box
    draw.rectangle([30, 310, 200, 380], fill=(250, 250, 250), outline=(150, 150, 150), width=1)
    draw.text((45, 370), "Signature", fill=(100, 100, 100), font=font_tiny)

    # Footer
    draw.rectangle([0, H - 50, W, H], fill=(0, 51, 102))
    draw.text((20, H - 38), "** DEMO ONLY — NOT A REAL DOCUMENT **", fill=(255, 200, 200), font=font_tiny)
    draw.text((W - 200, H - 38), "BharatShield Test Fixture", fill=(200, 200, 255), font=font_tiny)

    # QR placeholder (simple pattern)
    qr_x, qr_y = W - 130, H - 160
    draw.rectangle([qr_x, qr_y, qr_x + 100, qr_y + 100], outline=(0, 0, 0), width=2)
    # Simple QR-like pattern
    for i in range(3):
        for j in range(3):
            if (i + j) % 2 == 0:
                draw.rectangle(
                    [qr_x + 5 + i*32, qr_y + 5 + j*32,
                     qr_x + 32 + i*32, qr_y + 32 + j*32],
                    fill=(0, 0, 0)
                )

    # Save as high quality PNG — minimal compression artifacts
    out_path = OUTPUT_DIR / "clean_pan.png"
    img.save(str(out_path), format="PNG")
    print(f"Created: {out_path}")
    return str(out_path)


def create_tampered_aadhaar():
    """
    Create a synthetic Aadhaar-style card with deliberate tampering artifacts.

    Tampering method:
    1. Create base card
    2. Save as JPEG at very low quality (heavy artifact generation)
    3. Re-open and paste a "modified" region at different quality
    4. This creates ELA-detectable compression inconsistencies
    """
    W, H = 856, 540

    # ---- Step 1: Create base card ----
    img = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Aadhaar-style background
    draw.rectangle([0, 0, W, H], fill=(255, 255, 255))
    draw.rectangle([0, 0, W, 70], fill=(255, 153, 51))  # Saffron header

    font_large = _get_font(28)
    font_med = _get_font(20)
    font_small = _get_font(16)
    font_tiny = _get_font(13)

    draw.text((20, 15), "Government of India", fill="white", font=font_large)
    draw.text((20, 48), "आधार — Aadhaar", fill="white", font=font_small)

    # Photo box
    draw.rectangle([30, 90, 180, 240], fill=(220, 220, 220), outline=(80, 80, 80), width=2)
    draw.text((60, 155), "[PHOTO]", fill=(100, 100, 100), font=font_small)

    # Name
    draw.text((200, 90), "Name:", fill=(80, 80, 80), font=font_small)
    draw.text((200, 110), "PRIYA SINGH", fill=(10, 10, 10), font=font_med)

    # DOB (this is the "tampered" field)
    draw.text((200, 145), "Date of Birth:", fill=(80, 80, 80), font=font_small)

    # Gender
    draw.text((200, 190), "Gender:", fill=(80, 80, 80), font=font_small)
    draw.text((200, 208), "FEMALE", fill=(10, 10, 10), font=font_med)

    # Aadhaar number
    draw.text((200, 245), "Aadhaar No.:", fill=(80, 80, 80), font=font_small)
    draw.text((200, 265), "1234 5678 9012", fill=(10, 10, 10), font=_get_font(30))

    # Address
    draw.text((30, 260), "Address:", fill=(80, 80, 80), font=font_small)
    draw.text((30, 280), "123, Gandhi Nagar, Sector 7", fill=(30, 30, 30), font=font_small)
    draw.text((30, 300), "New Delhi - 110001", fill=(30, 30, 30), font=font_small)

    # Footer
    draw.rectangle([0, H - 50, W, H], fill=(19, 119, 59))  # Green
    draw.text((20, H - 38), "** DEMO ONLY — NOT A REAL DOCUMENT **", fill=(255, 220, 220), font=font_tiny)
    draw.text((W - 200, H - 38), "BharatShield Test Fixture", fill=(200, 255, 200), font=font_tiny)

    # ---- Step 2: Save as low-quality JPEG to introduce heavy artifacts ----
    base_buffer = io.BytesIO()
    img.save(base_buffer, format="JPEG", quality=30)  # Very low quality = heavy artifacts
    base_buffer.seek(0)
    base_img = Image.open(base_buffer).convert("RGB")

    # ---- Step 3: Create a "clean" patch (the tampered DOB area) ----
    # This simulates someone editing a specific region and saving differently
    patch = Image.new("RGB", (180, 30), color=(255, 255, 255))
    patch_draw = ImageDraw.Draw(patch)
    # Draw "modified" DOB at high quality
    patch_draw.text((2, 5), "01/01/1990", fill=(10, 10, 10), font=font_med)

    # Save patch at HIGH quality (different compression history = ELA detectable)
    patch_buffer = io.BytesIO()
    patch.save(patch_buffer, format="JPEG", quality=95)
    patch_buffer.seek(0)
    clean_patch = Image.open(patch_buffer).convert("RGB")

    # ---- Step 4: Paste the clean patch onto the degraded base ----
    # This creates compression inconsistency exactly where the DOB was "changed"
    base_img.paste(clean_patch, (200, 145))

    # ---- Step 5: Apply a slight blur to disguise the boundary ----
    # But this creates another forensic artifact
    region = base_img.crop((190, 140, 400, 185))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=0.5))
    base_img.paste(blurred, (190, 140))

    # Save final tampered image as PNG
    out_path = OUTPUT_DIR / "tampered_aadhaar.png"
    base_img.save(str(out_path), format="PNG")
    print(f"Created: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    print("Generating BharatShield demo test fixtures...")
    clean = create_clean_pan()
    tampered = create_tampered_aadhaar()
    print(f"\nDemo fixtures ready:")
    print(f"  Clean:    {clean}")
    print(f"  Tampered: {tampered}")
    print("\nExpected results (from actual forensic pipeline — NOT hardcoded):")
    print("  Clean:    High trust score, LOW risk (clean image, consistent compression)")
    print("  Tampered: Lower trust score, MEDIUM/HIGH risk (ELA detects patch inconsistency)")
