from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader


@dataclass
class PageText:
    page: int
    text: str


def extract_pages(path: Path) -> tuple[list[PageText], bool]:
    reader = PdfReader(str(path))
    pages: list[PageText] = []
    visible = 0
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        visible += len("".join(text.split()))
        pages.append(PageText(index, text))
    needs_ocr = visible < max(100, len(pages) * 30)
    return pages, needs_ocr
