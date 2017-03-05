import json
import re

from datetime import datetime, timedelta, timezone
from urllib import request
from xml.etree import ElementTree


class NsApi:
    ns_api_baseurl = "http://webservices.ns.nl/"

    def __init__(self, login, password):
        self.password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        self.password_mgr.add_password(None, self.ns_api_baseurl, login, password)

        self.handler = request.HTTPBasicAuthHandler(self.password_mgr)
        self.opener = request.build_opener(self.handler)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def fetch(self, url):
        return self.opener.open(self.ns_api_baseurl + url)

    def getStationsAsList(self):
        # http://webservices.ns.nl/ns-api-stations (English)
        # http://webservices.ns.nl/ns-api-stations-v2 (Dutch, but includes more aliases)
        response = self.fetch("ns-api-stations-v2")
        if (response.status != 200):
            raise("Could not fetch the list of stations.")

        response = response.read().decode('utf-8')
        tree = ElementTree.fromstring(response)

        stations = [];
        for station in tree:
            stations.append(station.find("Code").text)

            for name in [station.text for station in station.find("Namen")]:
                stations.append(name)

            for name in [station.text for station in station.find("Synoniemen")]:
                stations.append(name)

        stations.sort()
        return stations


    def getPossibleRoutes(self, fromStation, toStation, dateTime = datetime.now(), departureTime = True):
        params = "fromStation={0}&toStation={1}&dateTime={2}&departure={3}".format(fromStation, toStation,
            dateTime.strftime("%Y-%m-%dT%H:%M:%S"), departureTime)

        response = self.fetch("ns-api-treinplanner?" + params)
        if (response.status != 200):
            raise("Could not fetch a list of potential routes.")

        response = response.read().decode('utf-8')
        tree = ElementTree.fromstring(response)

        nowTime = datetime.now(tz = timezone(timedelta(hours=1)))

        for route in tree:
            departureTime = route.find("GeplandeVertrekTijd")
            departureTime = datetime.strptime(departureTime.text, "%Y-%m-%dT%H:%M:%S%z")

            travelTime = route.find("GeplandeReisTijd")

            # Iterate until we find a route that hasn't departed yet.
            if ((nowTime - departureTime).total_seconds() < 0):
                break;

        return (departureTime, travelTime.text)


    def getJourneyPrice(self, fromStation, toStation):
        params = "fromStation={0}&toStation={1}".format(fromStation, toStation)

        response = self.fetch("ns-api-prijzen-v3?" + params)
        if (response.status != 200):
            raise("Could not fetch the price for this journey.")

        raise("Not implemented")

    def compareList(self, list1, list2):
        for value in list1:
            if value in list2:
                return True
        return False

