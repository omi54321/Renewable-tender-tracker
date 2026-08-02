from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'KPCL'
    category = 'Karnataka'
    source_url = 'https://karnatakapower.com/'
