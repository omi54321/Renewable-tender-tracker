from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader


def extract_text(path: Path) -> tuple[str, bool]:
    reader = PdfReader(str(path))
    chunks = [(page.extract_text() or "") for page in reader.pages]
    text = "\n".join(chunks)
    visible = len("".join(text.split()))
    needs_ocr = visible < max(100, len(reader.pages) * 25)
    return text, needs_ocr
