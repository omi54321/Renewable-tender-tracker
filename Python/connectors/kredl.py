from __future__ import annotations

from Python.connectors.portals import NICPortalConnector, KPPPPortalConnector


class Connector(NICPortalConnector):
    agency = 'KREDL'
    category = 'Karnataka'
    source_url = 'https://kppp.karnataka.gov.in/'
