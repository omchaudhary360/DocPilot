import io
from pathlib import Path

import fitz
import pytesseract

from PIL import Image


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF.

    First tries normal PDF text extraction using PyMuPDF.
    If a page has little/no text, OCR is used as a fallback.
    """

    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        # Try normal text extraction
        text = page.get_text("text").strip()

        # If normal extraction returns little/no text,
        # use OCR on the rendered page image.
        if len(text) < 20:

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            image_bytes = pix.tobytes("png")

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            text = pytesseract.image_to_string(
                image
            ).strip()

        pages.append(
            {
                "page_number": page_number,
                "text": text
            }
        )

    document.close()

    return pages