from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'TANTRANSCO'
    category = 'Tamil Nadu'
    source_url = 'https://www.tantransco.gov.in/'
