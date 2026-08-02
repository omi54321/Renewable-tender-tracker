from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'GUVNL'
    category = 'Gujarat'
    source_url = 'https://www.guvnl.com/'
