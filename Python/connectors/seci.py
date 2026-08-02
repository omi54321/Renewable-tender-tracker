from __future__ import annotations

import re
from bs4 import BeautifulSoup

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = "SECI"
    category = "Central"
    source_url = "https://www.seci.co.in/tenders/"

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        records = []
        for row in soup.select("table tbody tr"):
            cells = [c.get_text(" ", strip=True) for c in row.select("td")]
            text = " | ".join(cells)
            if len(cells) < 4 or not self.is_relevant(text):
                continue
            links = row.select("a[href]")
            tender_id = next((x for x in cells if re.fullmatch(r"SECI\d+", x)), "")
            ref = next((x for x in cells if "SECI/" in x), tender_id or cells[0])
            records.append({
                "Tender ID": tender_id,
                "Category": self.category,
                "Agency": self.agency,
                "Tender Number": ref,
                "Title": text,
                "Tender URL": self.normalize_link(links[-1].get("href")) if links else self.source_url,
                "Document URL": self.find_document_url(links),
                "Raw Text": text,
                "Source Quality": "Official agency page",
            })
        return records
