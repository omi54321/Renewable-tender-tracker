from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from urllib.parse import urljoin
import logging
import re

from bs4 import BeautifulSoup

from Python.core.http import get_text


@dataclass
class ConnectorResult:
    agency: str
    source_url: str
    records: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    started: datetime = field(default_factory=datetime.utcnow)
    finished: datetime | None = None

    @property
    def status(self) -> str:
        return "Success" if not self.errors else ("Partial" if self.records else "Failed")


class BaseAgencyConnector(ABC):
    agency: str
    category: str
    source_url: str
    keywords = ("solar","wind","hybrid","fdre","rtc","bess","battery","storage","pumped storage","renewable")

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"connector.{self.agency}")

    @abstractmethod
    def parse(self, html: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fetch(self) -> str:
        return get_text(self.source_url)

    def run(self) -> ConnectorResult:
        result = ConnectorResult(self.agency, self.source_url)
        try:
            result.records = self.parse(self.fetch())
        except Exception as exc:
            self.logger.exception("Connector failed")
            result.errors.append(str(exc))
        result.finished = datetime.utcnow()
        return result

    def is_relevant(self, text: str) -> bool:
        return any(re.search(rf"\b{re.escape(keyword)}\b", text, re.I) for keyword in self.keywords)

    def normalize_link(self, href: str | None) -> str:
        return urljoin(self.source_url, href) if href else self.source_url


class HTMLTableConnector(BaseAgencyConnector):
    row_selectors = ("table tbody tr", "table tr", ".views-row", ".tender-item", "article")
    tender_number_patterns = (
        r"\b(?:RFS|RFP|NIT|TENDER|BID|GEM)[/\-A-Z0-9_.()]+",
        r"\b\d{4}_[A-Z]+_\d+_\d+\b",
    )

    def parse(self, html: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        seen: set[str] = set()
        records: list[dict[str, Any]] = []

        for selector in self.row_selectors:
            for row in soup.select(selector):
                text = " ".join(row.get_text(" ", strip=True).split())
                if len(text) < 15 or not self.is_relevant(text):
                    continue

                links = row.select("a[href]")
                url = self.normalize_link(links[0].get("href")) if links else self.source_url
                cells = [c.get_text(" ", strip=True) for c in row.select("th,td")]
                tender_number = self.extract_tender_number(text, cells)
                key = f"{tender_number}|{url}|{text[:120]}"
                if key in seen:
                    continue
                seen.add(key)

                records.append({
                    "Category": self.category,
                    "Agency": self.agency,
                    "Tender Number": tender_number,
                    "Title": " | ".join(cells[1:]) if len(cells) > 1 else text,
                    "Tender URL": url,
                    "Document URL": self.find_document_url(links),
                    "Raw Text": text,
                    "Source Quality": "Official agency page",
                })

            if records:
                break
        return records

    def extract_tender_number(self, text: str, cells: list[str]) -> str:
        for pattern in self.tender_number_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0)
        return cells[0][:150] if cells else text[:150]

    def find_document_url(self, links) -> str:
        for link in links:
            href = link.get("href", "")
            if href.lower().endswith(".pdf") or "download" in href.lower():
                return self.normalize_link(href)
        return ""
