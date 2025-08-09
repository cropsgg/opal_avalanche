from __future__ import annotations

from io import BytesIO
from typing import List, Tuple

import pytesseract
from PIL import Image


def has_text_layer(pdf_bytes: bytes) -> bool:
    # Placeholder: real implementation should inspect PDF objects
    return False


def ocr_image(img: Image.Image, lang: str = "eng+hin") -> str:
    return pytesseract.image_to_string(img, lang=lang)


def ocr_pdf_pages(pages: List[Image.Image], lang: str = "eng+hin") -> List[str]:
    return [ocr_image(p, lang=lang) for p in pages]


