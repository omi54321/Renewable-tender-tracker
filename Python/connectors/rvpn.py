from __future__ import annotations

from Python.connectors.base import HTMLTableConnector


class Connector(HTMLTableConnector):
    agency = 'RVPN'
    category = 'Rajasthan'
    source_url = 'https://energy.rajasthan.gov.in/rvpnl'
