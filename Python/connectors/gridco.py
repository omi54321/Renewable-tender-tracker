from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'GRIDCO'
    category = 'Odisha'
    source_url = 'https://www.gridco.co.in/tender.aspx'
