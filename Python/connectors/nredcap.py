from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'NREDCAP'
    category = 'Andhra Pradesh'
    source_url = 'https://nredcap.in/'
