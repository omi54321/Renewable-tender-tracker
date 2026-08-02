from __future__ import annotations

from Python.connectors.portals import NICPortalConnector, KPPPPortalConnector


class Connector(NICPortalConnector):
    agency = 'UPNEDA'
    category = 'Uttar Pradesh'
    source_url = 'https://upneda.org.in/'
