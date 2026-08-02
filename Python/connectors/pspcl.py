from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'PSPCL'
    category = 'Punjab'
    source_url = 'https://pspcl.in/tenders'
