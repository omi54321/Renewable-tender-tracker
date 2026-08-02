from __future__ import annotations

from typing import Any

from Python.connectors.base import HTMLTableConnector


class NICPortalConnector(HTMLTableConnector):
    """Best-effort public-listing connector for NIC eProcurement portals.

    CAPTCHA/session-gated result pages are reported through connector health rather
    than bypassed. Organisation-specific searches can be configured with a public URL.
    """

    row_selectors = (
        "#table tbody tr",
        "table.list_table tbody tr",
        "table tbody tr",
        ".list_table tr",
    )

    def fetch(self) -> str:
        # Public landing or saved public-search URL only.
        return super().fetch()


class KPPPPortalConnector(HTMLTableConnector):
    row_selectors = ("table tbody tr", ".card", ".tender-list-item")

    def fetch(self) -> str:
        return super().fetch()
