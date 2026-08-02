from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'MSEDCL'
    category = 'Maharashtra'
    source_url = 'https://www.mahadiscom.in/en/supplier/tenders/'
