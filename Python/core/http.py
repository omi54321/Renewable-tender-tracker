from __future__ import annotations

import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RenewableTenderTracker/12.0; automated-public-tender-monitor)"
}


def get_text(url: str, timeout: int = 45, retries: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Unable to fetch {url}: {last_error}")
