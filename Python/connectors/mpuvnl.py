from __future__ import annotations

from Python.connectors.portals import NICPortalConnector, KPPPPortalConnector


class Connector(NICPortalConnector):
    agency = 'MPUVNL'
    category = 'Madhya Pradesh'
    source_url = 'https://mptenders.gov.in/nicgep/app'
