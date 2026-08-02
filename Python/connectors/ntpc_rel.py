from __future__ import annotations

from bs4 import BeautifulSoup

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = "NTPC REL"
    category = "Central"
    source_url = "https://ntpctender.ntpc.co.in/Index/Search?Region=10&Type=Reg"

    def parse(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        records = []
        for row in soup.select("table tbody tr"):
            cells = [c.get_text(" ", strip=True) for c in row.select("td")]
            text = " | ".join(cells)
            if not cells or not self.is_relevant(text):
                continue
            links = row.select("a[href]")
            records.append({
                "Category": self.category,
                "Agency": self.agency,
                "Tender Number": cells[0],
                "Title": cells[2] if len(cells) > 2 else text,
                "Tender URL": self.normalize_link(next((a.get("href") for a in links if "NITDetails" in a.get("href","")), None)),
                "Document URL": self.find_document_url(links),
                "Raw Text": text,
                "Source Quality": "Official agency page",
            })
        return records
