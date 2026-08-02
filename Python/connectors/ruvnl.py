from __future__ import annotations

from Python.connectors.portals import NICPortalConnector, KPPPPortalConnector


class Connector(NICPortalConnector):
    agency = 'RUVNL'
    category = 'Rajasthan'
    source_url = 'https://eproc.rajasthan.gov.in/nicgep/app'
