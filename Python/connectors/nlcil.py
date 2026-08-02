from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'NLCIL'
    category = 'Central'
    source_url = 'https://www.nlcindia.in/'
