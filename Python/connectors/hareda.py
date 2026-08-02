from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'HAREDA'
    category = 'Haryana'
    source_url = 'https://hareda.gov.in/'
