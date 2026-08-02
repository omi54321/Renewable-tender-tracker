from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'GPCL'
    category = 'Gujarat'
    source_url = 'https://gpcl.gujarat.gov.in/'
