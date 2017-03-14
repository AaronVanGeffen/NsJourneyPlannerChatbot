import json
import re

from datetime import datetime, timedelta, timezone
from urllib import request
from urllib.parse import urlencode
from xml.etree import ElementTree


class NsApi:
    ns_api_baseurl = "http://webservices.ns.nl/"

    def __init__(self, login, password, verbose = False):
        self.password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
        self.password_mgr.add_password(None, self.ns_api_baseurl, login, password)

        self.handler = request.HTTPBasicAuthHandler(self.password_mgr)
        self.opener = request.build_opener(self.handler)

        self.verbose = verbose

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def fetch(self, url):
        if self.verbose:
            print (self.ns_api_baseurl + url)
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

        return sorted(set(stations))


    def findSuitableRoute(self, requestedTime, availableRoutes):
        for route in availableRoutes:
            departureTime = route.find("GeplandeVertrekTijd")
            departureTime = datetime.strptime(departureTime.text, "%Y-%m-%dT%H:%M:%S%z")

            # Iterate until we find a route that hasn't departed yet.
            if ((requestedTime - departureTime).total_seconds() < 0):
                return (departureTime, route)

        raise Exception("No suitable route found in set.")


    def getPossibleRoutes(self, fromStation, toStation, requestTime = datetime.now(tz = timezone(timedelta(hours=1))), departureTime = True):
        params = {'fromStation': fromStation, 'toStation': toStation,
            'dateTime': requestTime.strftime("%Y-%m-%dT%H:%M:%S"), 'departureTime': departureTime}
        params = urlencode(params)

        response = self.fetch("ns-api-treinplanner?" + params)
        if (response.status != 200):
            raise Exception("Could not fetch a list of potential routes.")

        response = response.read().decode('utf-8')
        tree = ElementTree.fromstring(response)

        (departureTime, route) = self.findSuitableRoute(requestTime, tree.findall('ReisMogelijkheid'))

        journey = []
        for track in route.findall('ReisDeel'):
            stops = track.findall('ReisStop')
            firstStop = stops[0]
            lastStop = stops[-1]

            journey.append({
                'startStation': firstStop.find('Naam').text,
                'startTime': datetime.strptime(firstStop.find('Tijd').text, "%Y-%m-%dT%H:%M:%S%z"),
                'startPlatform': firstStop.find('Spoor').text,
                'endStation': lastStop.find('Naam').text,
                'endTime': datetime.strptime(lastStop.find('Tijd').text, "%Y-%m-%dT%H:%M:%S%z"),
                'endPlatform': lastStop.find('Spoor').text,
            })

        status = route.find("Status").text

        # Any delay?
        if status == "VERTRAAGD":
            delay = route.find("AankomstVertraging").text
        else:
            delay = ''

        return {
            'fromStation': fromStation,
            'toStation': toStation,
            'departureTime': departureTime,
            'travelTime': route.find("GeplandeReisTijd").text,
            'actualTime': route.find("ActueleReisTijd").text,
            'numTransfers': int(route.find("AantalOverstappen").text),
            'currentDelay': delay,
            'status': status,
            'isDelayed': status == "VERTRAAGD",
            'isNormal':  status == "VOLGENS-PLAN",
            'journey': journey,
        }


    def getJourneyPrice(self, fromStation, toStation):
        params = {'fromStation': fromStation, 'toStation': toStation}
        params = urlencode(params)

        response = self.fetch("ns-api-prijzen-v3?" + params)
        if (response.status != 200):
            raise Exception("Could not fetch the price for this journey.")

        # Keeps yielding 'unauthorized' errors, so we'll skip this for now.
        raise("Not implemented")
