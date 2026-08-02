from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'REMCL'
    category = 'Central'
    source_url = 'https://www.remcl.in/'
