from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'MAHAGENCO'
    category = 'Maharashtra'
    source_url = 'https://www.mahagenco.in/'
