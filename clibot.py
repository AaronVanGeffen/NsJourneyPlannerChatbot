#!/usr/bin/env python3
from NsApi import NsApi

API_LOGIN    = ""
API_PASSWORD = ""

ns = NsApi(API_LOGIN, API_PASSWORD)

stations = ns.getStationsAsList()

ns.getJourneyPrice("Nm", "Ut")
ns.getPossibleRoutes("Nm", "Ut")
