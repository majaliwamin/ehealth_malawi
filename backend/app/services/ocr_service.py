import io
import os
import re
import logging
from pathlib import Path
from typing import Optional
import tempfile

logger = logging.getLogger(__name__)

TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- import OCR engines (graceful) ----------
_HAVE_TESSERACT = False
_HAVE_EASYOCR = False
_HAVE_PADDLEOCR = False
_HAVE_CV = False

try:
    import pytesseract
    if os.path.exists(TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    _HAVE_TESSERACT = True
except Exception:
    pass

try:
    import easyocr
    _EASY_READER = None
    _HAVE_EASYOCR = True
except Exception:
    pass

try:
    import paddleocr
    _PADDLE_OCR = None
    _HAVE_PADDLEOCR = True
except Exception:
    pass

try:
    import cv2
    import numpy as np
    _HAVE_CV = True
except Exception:
    pass

try:
    import fitz
    _HAVE_FITZ = True
except Exception:
    _HAVE_FITZ = False


# ---------- image preprocessing ----------
def preprocess_image(image_bytes: bytes) -> bytes:
    if not _HAVE_CV:
        return image_bytes
    try:
        import numpy as np
        import cv2
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return image_bytes

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)

        # Sharpening kernel
        sharpen = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, sharpen)

        # Try Otsu first; if image is mostly background, fall back to adaptive
        otsu_val, otsu_thresh = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        white_frac = cv2.countNonZero(otsu_thresh) / (otsu_thresh.shape[0] * otsu_thresh.shape[1])

        if 0.2 < white_frac < 0.9:
            thresh = otsu_thresh
        else:
            # Adaptive Gaussian thresholding as fallback
            thresh = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 31, 4)

        # Morphological opening to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Upscale 2x
        scale = 2.0
        w = int(cleaned.shape[1] * scale)
        h = int(cleaned.shape[0] * scale)
        resized = cv2.resize(cleaned, (w, h), interpolation=cv2.INTER_CUBIC)

        success, buf = cv2.imencode(".png", resized)
        if success:
            return buf.tobytes()
    except Exception as e:
        logger.warning("Image preprocessing failed: %s", e)
    return image_bytes


# ---------- Tesseract ----------
def ocr_tesseract(image_bytes: bytes, lang: str = "eng") -> Optional[str]:
    if not _HAVE_TESSERACT:
        return None
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        config = "--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.:/+-%<>=, "
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        text = text.strip()
        return text if text else None
    except Exception as e:
        logger.warning("Tesseract OCR failed: %s", e)
        return None


# ---------- EasyOCR ----------
def ocr_easyocr(image_bytes: bytes, lang: str = "en") -> Optional[str]:
    if not _HAVE_EASYOCR:
        return None
    global _EASY_READER
    try:
        import easyocr
        if _EASY_READER is None:
            _EASY_READER = easyocr.Reader([lang], gpu=False)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmppath = tmp.name
        try:
            results = _EASY_READER.readtext(tmppath, detail=0, paragraph=True)
        finally:
            try:
                os.unlink(tmppath)
            except Exception:
                pass
        text = "\n".join(results).strip()
        return text if text else None
    except Exception as e:
        logger.warning("EasyOCR failed: %s", e)
        return None


# ---------- PaddleOCR ----------
def ocr_paddleocr(image_bytes: bytes, lang: str = "en") -> Optional[str]:
    if not _HAVE_PADDLEOCR:
        return None
    global _PADDLE_OCR
    try:
        from paddleocr import PaddleOCR
        if _PADDLE_OCR is None:
            _PADDLE_OCR = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False, use_gpu=False)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmppath = tmp.name
        try:
            result = _PADDLE_OCR.ocr(tmppath, cls=True)
        finally:
            try:
                os.unlink(tmppath)
            except Exception:
                pass
        if not result or not result[0]:
            return None
        lines = []
        for line_group in result:
            for line in line_group:
                text = line[1][0] if isinstance(line, (list, tuple)) and len(line) > 1 else str(line)
                lines.append(text)
        text = "\n".join(lines).strip()
        return text if text else None
    except Exception as e:
        logger.warning("PaddleOCR failed: %s", e)
        return None


# ---------- PDF text extraction (PyMuPDF) ----------
def extract_pdf_text(image_bytes: bytes) -> Optional[str]:
    if not _HAVE_FITZ:
        return None
    try:
        import fitz
        doc = fitz.open(stream=image_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text = page.get_text()
            if text.strip():
                text_parts.append(text.strip())
            else:
                # Rasterise page and fall back to OCR
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                ocr_result = ocr_tesseract(img_bytes)
                if ocr_result:
                    text_parts.append(ocr_result)
        doc.close()
        full = "\n".join(text_parts).strip()
        return full if full else None
    except Exception as e:
        logger.warning("PDF text extraction failed: %s", e)
        return None


# ---------- main OCR ----------
def ocr_image(image_bytes: bytes, lang: str = "eng") -> dict:
    # Try PDF text extraction first (if it's a PDF, no OCR needed)
    pdf_text = extract_pdf_text(image_bytes)
    if pdf_text and len(pdf_text) > 5:
        return {
            "success": True,
            "engine_used": "pymupdf",
            "text": pdf_text,
            "fallback_attempted": False,
            "all_engines": {"pymupdf": pdf_text},
        }

    preprocessed = preprocess_image(image_bytes)
    engines = []

    if _HAVE_TESSERACT:
        engines.append(("tesseract", lambda: ocr_tesseract(preprocessed, lang)))
    if _HAVE_EASYOCR:
        eng_lang = "en" if lang == "eng" else lang
        engines.append(("easyocr", lambda: ocr_easyocr(preprocessed, eng_lang)))
    if _HAVE_PADDLEOCR:
        eng_lang = "en" if lang == "eng" else lang
        engines.append(("paddleocr", lambda: ocr_paddleocr(preprocessed, eng_lang)))

    if not engines:
        return {
            "success": False,
            "engine_used": None,
            "text": None,
            "error": "No OCR engine available. Install pytesseract, easyocr, or paddleocr.",
        }

    results = []
    for name, fn in engines:
        try:
            text = fn()
            if text and len(text) > 5:
                results.append((name, text))
        except Exception as e:
            logger.warning("Engine %s error: %s", name, e)

    if results:
        best = results[0]
        return {
            "success": True,
            "engine_used": best[0],
            "text": best[1],
            "fallback_attempted": len(engines) > 1,
            "all_engines": {n: t for n, t in results},
        }

    return {
        "success": False,
        "engine_used": engines[0][0] if engines else None,
        "text": None,
        "error": "All OCR engines returned empty text.",
    }
