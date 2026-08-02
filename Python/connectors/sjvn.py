from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'SJVN'
    category = 'Central'
    source_url = 'https://sjvn.nic.in/en/tender'
