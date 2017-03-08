#!/usr/bin/env python3
from enum  import Enum
from NsApi import NsApi

import re


class NsBot:
    def __init__(self, login, password):
        self.ns = NsApi(login, password)

        self.knownStations      = self.ns.getStationsAsList()
        self.knownStationsLower = [x.lower() for x in self.knownStations]

        self.reReplyDeptStation  = re.compile("^.*?(van(?:uit)?|from)\s(?P<fromStation>['\-A-z ]+).*?$", re.IGNORECASE)
        self.reReplyDestStation  = re.compile("^.*?(naar|to)\s(?P<toStation>['\-A-z ]+).*?$", re.IGNORECASE)
        self.rePlanJourney1 = re.compile("^.*?(?:van(?:uit)?|from)\s(?P<fromStation>['\-A-z ]+?)\s(?:naar|to)\s(?P<toStation>['\-A-z ]+).*?$", re.IGNORECASE)
        self.rePlanJourney2 = re.compile("^.*?(?:naar|to)?\s(?P<toStation>['\-A-z ]+?)\s(?:van(?:uit)?|from)\s(?P<fromStation>['\-A-z ]+).*?$", re.IGNORECASE)


    def getStationInfoFromMsg(self, msg):
        matches = self.rePlanJourney1.match(msg)
        if matches == None:
           matches = self.rePlanJourney2.match(msg)

        if matches != None:
            stations = {
                'departure': matches.group('fromStation'),
                'destination': matches.group('toStation')
            }

        else:
            matches = self.reReplyDeptStation.match(msg)
            if matches != None:
                stations = {
                    'departure': matches.group('fromStation')
                }

            else:
                matches = self.reReplyDestStation.match(msg)
                if matches != None:
                    stations = {
                        'destination': matches.group('toStation')
                    }

                else:
                    stations = {}

        return stations


    def validateStations(self, stations):
        valid = {}
        for what in ['departure', 'destination']:
            if what in stations:
                station = stations[what].lower()
                try:
                    index = self.knownStationsLower.index(station)
                    valid[what] = self.knownStations[index]
                except ValueError:
                    continue

        return valid


    def resetMemory(self):
        self.memory = {}


    def commitToMemory(self, stuff):
        self.memory.update(stuff)


    def chat(self):
        print ("Hello! Welcome to NS, the Dutch Railways! 🚃🚃🚃")
        print ("Where would you like to go today?")
        print ("(Use ^D to quit)")

        self.resetMemory()

        userInput = '🚃'
        while userInput != '':
            try:
                userInput = input("\n>>> ")
                print ()
            except EOFError:
                print ("\nBye!")
                return

            # TODO: only accept these in certain chat state
            stations = self.getStationInfoFromMsg(userInput)
            stations = self.validateStations(stations)

            if len(stations):
                self.commitToMemory(stations)
            else:
                print ("Hmm, sorry, I don't quite understand what you mean.")
                continue

            # Do we have all the ingredients we need to give a journey advice?
            if 'departure' in self.memory and 'destination' in self.memory:
                route = self.ns.getPossibleRoutes(self.memory['departure'], self.memory['destination'])

                # Give them the basic run-down.
                print ("The next train to {toStation} departs at {0} from station {fromStation}, platform X ".format(
                    route['departureTime'].strftime("%H:%M"),
                    **route
                ))

                # Any transfers they need to be aware of?
                if route['numTransfers'] == 1:
                    print ("You will have to transfer once.")
                elif route['numTransfers'] > 1:
                    print ("You will have to transfer %s times." % (str(route['numTransfers'])))

                print ("Planned travel time is %s." % (route['travelTime']))

                # Is the train delayed?
                if route['isDelayed']:
                    print ("Note: the train is currently delayed by %s." % route['currentDelay'])

                # Blurt out the whole report.
                # TODO: make this optional or requestable?
                currentSegment = 0
                for track in route['journey']:
                    currentSegment += 1
                    print ("({0}/{1}) {startStation} platform {startPlatform} at {2} 👉 {endStation} platform {endPlatform} at {3}".format(
                        currentSegment,
                        len(route['journey']),
                        track['startTime'].strftime("%H:%M"),
                        track['endTime'].strftime("%H:%M"),
                        **track
                    ))

            # Just the departure station?
            elif 'departure' in self.memory:
                print ("Alright, where would you like to go?")

            # Just the destination station?
            elif 'destination' in self.memory:
                print ("Okay. From which station would you like to depart?")


API_LOGIN    = ""
API_PASSWORD = ""


ns = NsBot(API_LOGIN, API_PASSWORD)
ns.chat()


#ns.getJourneyPrice("Nm", "Ut")
#departureTime, route = ns.getPossibleRoutes("Nm", "Ut")

#departureTime = route.find("GeplandeVertrekTijd")

