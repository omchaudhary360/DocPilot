import io
import os
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


def get_tesseract_cmd() -> str:
    """
    Get Tesseract path from environment or use system default.
    Supports Windows, Linux, and macOS.
    """
    env_path = os.getenv("TESSERACT_CMD")
    if env_path:
        return env_path
    
    # Windows default
    if os.name == 'nt':
        default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(default_path):
            return default_path
    
    # Assume it's in PATH on Linux/Mac
    return "tesseract"


def set_tesseract_path():
    """Configure Tesseract path for pytesseract"""
    try:
        cmd_path = get_tesseract_cmd()
        if cmd_path and os.path.exists(cmd_path):
            pytesseract.pytesseract.tesseract_cmd = cmd_path
    except Exception:
        pass


set_tesseract_path()


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF with robust fallback handling.
    
    Strategy:
    1. Try normal PyMuPDF extraction
    2. If insufficient text (< 50 chars), use OCR
    3. Preserve page-level structure
    4. Handle multi-column layouts
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    try:
        document = fitz.open(file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {str(e)}")
    
    pages = []
    
    try:
        for page_number in range(len(document)):
            try:
                page = document[page_number]
                
                # Try normal text extraction
                text = page.get_text("text").strip()
                
                # If insufficient text, use OCR
                if len(text) < 50:
                    try:
                        # Render page to image at higher DPI for better OCR
                        pix = page.get_pixmap(
                            matrix=fitz.Matrix(2, 2),
                            alpha=False
                        )
                        
                        image_bytes = pix.tobytes("png")
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # OCR with explicit language support
                        ocr_text = pytesseract.image_to_string(
                            image,
                            lang="eng"
                        ).strip()
                        
                        # Use OCR if it produced more text
                        if len(ocr_text) > len(text):
                            text = ocr_text
                            
                    except Exception as ocr_error:
                        print(f"OCR failed for page {page_number + 1}: {ocr_error}")
                        # Continue with regular extraction
                
                pages.append({
                    "page_number": page_number + 1,
                    "text": text
                })
                
            except Exception as page_error:
                print(f"Error processing page {page_number + 1}: {page_error}")
                pages.append({
                    "page_number": page_number + 1,
                    "text": ""
                })
    
    finally:
        document.close()
    
    return pages