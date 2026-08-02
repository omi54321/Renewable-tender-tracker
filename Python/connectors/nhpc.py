from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'NHPC'
    category = 'Central'
    source_url = 'https://www.nhpcindia.com/welcome/tender.html'
