from __future__ import annotations

from Python.connectors.portals import NICPortalConnector, KPPPPortalConnector


class Connector(NICPortalConnector):
    agency = 'BSPHCL'
    category = 'Bihar'
    source_url = 'https://www.bsphcl.co.in/'
