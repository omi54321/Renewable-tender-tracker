from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'KPTCL'
    category = 'Karnataka'
    source_url = 'https://kptcl.karnataka.gov.in/'
