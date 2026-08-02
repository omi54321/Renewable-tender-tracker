from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin
import re

from bs4 import BeautifulSoup

from Python.core.http import get_text


@dataclass
class GenericConnector:
    agency: str
    category: str
    source_url: str

    def run(self) -> list[dict]:
        html = get_text(self.source_url)
        soup = BeautifulSoup(html, "html.parser")
        records: list[dict] = []

        for row in soup.select("table tr, .tender-item, .views-row, article"):
            text = row.get_text(" ", strip=True)
            if not re.search(r"\b(tender|rfs|rfp|nit|bid|bess|fdre|solar|wind|hybrid)\b", text, re.I):
                continue

            cells = [c.get_text(" ", strip=True) for c in row.select("th,td")]
            links = row.select("a[href]")
            url = urljoin(self.source_url, links[0]["href"]) if links else self.source_url
            tender_number = cells[0] if cells else text[:80]
            title = " | ".join(cells[1:]) if len(cells) > 1 else text

            records.append({
                "Category": self.category,
                "Agency": self.agency,
                "Tender Number": tender_number,
                "Title": title,
                "Tender URL": url,
                "Raw Text": text,
            })

        return records
