#!/usr/bin/env python3
from enum  import Enum
from NsApi import NsApi
from datetime import datetime, timedelta, timezone

import argparse
import re


class NsBot:
    def __init__(self, login, password, verbose = False):
        self.ns = NsApi(login, password)
        self.verbose = verbose

        self.knownStations      = self.ns.getStationsAsList()
        self.knownStationsLower = [x.lower() for x in self.knownStations]

        self.knownStations.sort(key = len, reverse = True)
        escStations = [re.escape(station) for station in self.knownStations]
        expStations = '|'.join(escStations)

        self.reReplyDeptStation = re.compile("^.*(van(?:uit)?|from)\s(?P<fromStation>" + expStations + ").*$", re.IGNORECASE)
        self.reReplyDestStation = re.compile("^.*(naar|to)\s(?P<toStation>" + expStations + ").*$", re.IGNORECASE)

        self.reGreeting = re.compile("^.*(hallo|hoi|goede\s*(morgen?|middag|avond)|" +
                                           "hello|hi|good\s*(morning|afternoon|evening)).*$", re.IGNORECASE)

        self.reThanks = re.compile("^.*(bedankt|dankjewel|dankje|danku|dank u|thank|thanks).*$", re.IGNORECASE)

        self.reGoodbye = re.compile("^.*(bye|goodbye|farewell|doeg|doei|dag|houdoe|mazzel).*$", re.IGNORECASE)

        self.reReplyTime = re.compile("^.*?(?P<kind>arrive|depart|vertrek|aankom(?:en:st))?\s*" +
                                      "(?:at|om)\s*(?P<hour>\d+):(?P<minute>\d+).*?$", re.IGNORECASE)


    def getStationInfoFromMsg(self, msg):
        stations = {}

        matches = self.reReplyDeptStation.match(msg)
        if matches != None:
            stations.update({
                'departure': matches.group('fromStation')
            })

        matches = self.reReplyDestStation.match(msg)
        if matches != None:
            stations.update({
                'destination': matches.group('toStation')
            })

        return stations


    def getTimeInfoFromMsg(self, msg):
        timeMatch = self.reReplyTime.match(msg)
        if timeMatch == None and (msg == "nu" or msg == "now"):
            return {
                'time': datetime.now(tz = timezone(timedelta(hours=1))),
                'isDepartureTime': True,
            }

        elif timeMatch == None:
            return {}

        else:
            isDepartureTime = timeMatch.group('kind') in ['depart', 'vertrek', '']

            timestamp = datetime.now(tz = timezone(timedelta(hours=1)))
            timestamp = timestamp.replace(hour = int(timeMatch.group('hour')),
                                          minute = int(timeMatch.group('minute')))
            return {
                'time': timestamp,
                'isDepartureTime': isDepartureTime,
            }


    def containsGreeting(self, msg):
        return self.reGreeting.match(msg) != None


    def containsThanks(self, msg):
        return self.reThanks.match(msg) != None


    def containsGoodbye(self, msg):
        return self.reGoodbye.match(msg) != None


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

            # Did they just greet us? Politely return the favour.
            if self.containsGreeting(userInput):
                print ("Hello there!")
                hasSimpleMessage = True

            # Or did they just thank us? Who knows why, but let's be polite.
            elif self.containsThanks(userInput):
                print ("Oh, you're very welcome!")
                hasSimpleMessage = True

            # Are they saying farewell? Then let's part ways.
            elif self.containsGoodbye(userInput):
                print ("Bye bye! See you next time!")
                hasSimpleMessage = True
                return

            # Alas, things aren't as simple as they seem, this time!
            else:
                hasSimpleMessage = False


            # TODO: only accept these in certain chat state
            stations = self.getStationInfoFromMsg(userInput)
            time = self.getTimeInfoFromMsg(userInput)

            if len(stations):
                self.commitToMemory(stations)

            if len(time):
                self.commitToMemory(time)

            if self.verbose:
                print ("Memory now: ", self.memory)

            if not len(stations) and not len(time):
                if not hasSimpleMessage:
                    print ("Hmm, sorry, I don't quite understand what you mean.")
                continue

            # Do we have all the ingredients we need to give a journey advice?
            if 'departure' in self.memory and 'destination' in self.memory and 'time' in self.memory:
                try:
                    route = self.ns.getPossibleRoutes(self.memory['departure'], self.memory['destination'],
                                    self.memory['time'], self.memory['isDepartureTime'])
                except Exception:
                    print ("No suitable route could be found between %s and %s. Sorry!" %
                        (self.memory['departure'], self.memory['destination']))
                    continue

                # Give them the basic run-down.
                print ("The next train to {toStation} departs at {0} from station {fromStation}".format(
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

            # So we have our stations, just no time yet?
            elif 'time' in self.memory:
                print ("Alright! Where would you like to go?")

            # Or is it just the departure or arrival time we're lacking?
            elif not 'time' in self.memory:
                print ("Great! When do you want to leave?")


# Optionally run the bot.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Chatbot for Dutch Railways using command-line interaction.', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--login', required = True, help = 'your API account email address')
    parser.add_argument('-p', '--password', required = True, help = 'your API account password')
    parser.add_argument('-v', '--verbose', default = False, help = "increase output verbosity", action = "store_true")

    # Fetch command line arguments.
    args = parser.parse_args()

    # Run the bot.
    ns = NsBot(args.login, args.password, args.verbose)
    ns.chat()
