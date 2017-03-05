#!/usr/bin/env python3
from enum  import Enum
from NsApi import NsApi

import re


class NsBot:
    def __init__(self, login, password):
        self.ns = NsApi(login, password)

        self.knownStations      = self.ns.getStationsAsList()
        self.knownStationsLower = [x.lower() for x in self.knownStations]

        self.reReplyDeptStation  = re.compile("(van(?:uit)?|from)\s(?P<fromStation>['\-A-z]+)")
        self.reReplyDestStation  = re.compile("(naar|to)\s(?P<toStation>['\-A-z]+)")
        self.rePlanJourney1 = re.compile("(?:van(?:uit)?|from)\s(?P<fromStation>['\-A-z]+)\s(?:naar|to)\s(?P<toStation>['\-A-z ]+)")
        self.rePlanJourney2 = re.compile("(?:naar|to)?\s(?P<toStation>['\-A-z]+)\s(?:van(?:uit)?|from)\s(?P<fromStation>['\-A-z ]+)")


    def compareList(self, list1, list2):
        for value in list1:
            if value in list2:
                return True
        return False


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

        print (stations)
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

        print (valid)
        return valid


    def resetMemory(self):
        self.memory = {}


    def commitToMemory(self, stuff):
        self.memory.update(stuff)


    def chat(self):
        planningList = ["plan", "planning"]
        quitList = ["quit", "stop"]
        confirmList = ["yes", "yeah", "yep", "sure", "y"]
        denyList = ["no", "nope", "n"]

        print ("Hello! Welcome to NS, the Dutch Railways! 🚃🚃🚃")
        print ("Where would you like to go today?")

        self.resetMemory()

        while True:
            userInput = input(">>> ")
            input_list = userInput.split()

            # TODO: only accept these in certain chat state
            stations = self.getStationInfoFromMsg(userInput)
            stations = self.validateStations(stations)
            self.commitToMemory(stations)

            if self.compareList(input_list, planningList):
                print("From which station do you want to take the train?")
                departureStation = input(">>> ")
                if self.compareList(departureStation.lower().split(), self.knownStationsLower):
                    print("Valid station")

                print("Where do you want to go?")
                arrivalStation = input(">>> ")
                if self.compareList(arrivalStation.lower().split(), self.knownStationsLower):
                    print("Valid station")

                departureTime, travelTime = self.ns.getPossibleRoutes(departureStation, arrivalStation)
                print("The train from %s to %s leaves at %s from platform X" % (departureStation, arrivalStation, departureTime.strftime("%H:%M")))

                print("Would you like to know how long this trip is?")
                userInput = input(">>> ")
                if self.compareList(userInput, confirmList):
                    print("The expected travel time is: %s" %travelTime)

            if self.compareList(input_list, quitList):
                print("Goodbye!")
                return



API_LOGIN    = ""
API_PASSWORD = ""


ns = NsBot(API_LOGIN, API_PASSWORD)
ns.chat()


#ns.getJourneyPrice("Nm", "Ut")
#departureTime, route = ns.getPossibleRoutes("Nm", "Ut")

#departureTime = route.find("GeplandeVertrekTijd")

