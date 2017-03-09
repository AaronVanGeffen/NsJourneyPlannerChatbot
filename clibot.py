#!/usr/bin/env python3
from enum  import Enum
from NsApi import NsApi
from datetime import datetime, timedelta, timezone

import argparse
import re


class ChatQuestions(Enum):
    ARRIVAL = 1
    DEPARTURE = 2
    TIME = 3


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

        self.reGreeting = re.compile("^.*(hallo|hoi|goeden?\s*(morgen?|middag|avond)|" +
                                           "hello|hi|good\s*(morning|afternoon|evening)).*$", re.IGNORECASE)

        self.reThanks = re.compile("^.*(bedankt|dankjewel|dankje|danku|dank u|thank|thanks).*$", re.IGNORECASE)

        self.reGoodbye = re.compile("^.*(bye|goodbye|farewell|doeg|doei|dag|houdoe|mazzel).*$", re.IGNORECASE)

        self.reReplyTime = re.compile("^.*?(?P<kind>arrive|depart|vertrek|aankom(?:en:st))?\s*" +
                                      "(?:at|om|rond)\s*(?P<hour>\d+):(?P<minute>\d+).*?$", re.IGNORECASE)


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


    def isAValidStation(self, msg):
        return msg.lower() in self.knownStationsLower


    def isAValidTimestamp(self, msg):
        test = re.compile('^\d{1,2}:\d{2}$')
        return test.match(msg) != None


    def containsGreeting(self, msg):
        return self.reGreeting.match(msg) != None


    def containsThanks(self, msg):
        return self.reThanks.match(msg) != None


    def containsGoodbye(self, msg):
        return self.reGoodbye.match(msg) != None


    def resetMemory(self):
        self.memory = {
            'lastQuestion': -1
        }


    def commitToMemory(self, stuff):
        self.memory.update(stuff)


    def allSetForJourneyAdvice(self):
        return 'departure' in self.memory and 'destination' in self.memory and 'time' in self.memory


    def sendReply(self, msg):
        print (msg)


    def chatLoop(self):
        self.sendReply("Hello! Welcome to NS, the Dutch Railways! 🚃🚃🚃")
        self.sendReply("Where would you like to go today?")
        self.sendReply("(Use ^D to quit)")

        self.resetMemory()

        while True:
            try:
                message = input("\n>>> ")
                if not self.handleMessage(message):
                    return

            except EOFError:
                self.sendReply("\nBye!")
                return


    def handleMessage(self, message):
            # Did they just greet us? Politely return the favour.
            if self.containsGreeting(message):
                self.sendReply("Hello there!")
                isSimpleMessage = True

            # Or did they just thank us? Who knows why, but let's be polite.
            elif self.containsThanks(message):
                self.sendReply("Oh, you're very welcome!")
                isSimpleMessage = True

            # Are they saying farewell? Then let's part ways.
            elif self.containsGoodbye(message):
                self.sendReply("Bye bye! See you next time!")
                isSimpleMessage = True
                return False

            # Alas, things aren't as simple as they seem, this time!
            else:
                isSimpleMessage = False

            # Try and get as many info about our route.
            stations = self.getStationInfoFromMsg(message)
            if len(stations):
                isSimpleMessage = False
                self.commitToMemory(stations)

            # And indeed, when we arrive or depart.
            time = self.getTimeInfoFromMsg(message)
            if len(time):
                isSimpleMessage = False
                self.commitToMemory(time)

            # A few more tricks: are we replying with a valid station name?
            if self.isAValidStation(message):
                if self.memory['lastQuestion'] == ChatQuestions.ARRIVAL:
                    self.sendReply("Alright, going to %s! Lovely." % message)
                    self.commitToMemory({'destination': message})

                elif self.memory['lastQuestion'] == ChatQuestions.DEPARTURE:
                    self.sendReply("Alright, departing at %s." % message)
                    self.commitToMemory({'departure': message})

                else:
                    self.sendReply("Lovely station, %s, but what about it?" % message)
                    return True

            # Another one: are we just replying with a time?
            elif self.isAValidTimestamp(message):
                if self.memory['lastQuestion'] == ChatQuestions.TIME:
                    self.sendReply("Alright, departing at %s!" % message)
                    self.commitToMemory({'time': message, 'isDepartureTime': True})

                else:
                    self.sendReply("That's a wonderful time. What about it, though?")
                    return True

            elif isSimpleMessage:
                return True

            if self.verbose:
                self.sendReply("Memory now: ", self.memory)

            # Do we have all the ingredients we need to give a journey advice?
            if self.allSetForJourneyAdvice():
                try:
                    route = self.ns.getPossibleRoutes(self.memory['departure'], self.memory['destination'],
                                    self.memory['time'], self.memory['isDepartureTime'])
                except Exception:
                    self.sendReply("No suitable route could be found between %s and %s. Sorry!" %
                        (self.memory['departure'], self.memory['destination']))
                    return True

                # Give them the basic run-down.
                self.sendReply("The next train to {toStation} departs at {0} from station {fromStation}.".format(
                    route['departureTime'].strftime("%H:%M"),
                    **route
                ))

                # Any transfers they need to be aware of?
                if route['numTransfers'] == 1:
                    self.sendReply("You will have to transfer once.")
                elif route['numTransfers'] > 1:
                    self.sendReply("You will have to transfer %s times." % (str(route['numTransfers'])))

                self.sendReply("Planned travel time is %s." % (route['travelTime']))

                # Is the train delayed?
                if route['isDelayed']:
                    self.sendReply("Note: the train is currently delayed by %s." % route['currentDelay'])

                # Blurt out the whole report.
                # TODO: make this optional or requestable?
                currentSegment = 0
                for track in route['journey']:
                    currentSegment += 1
                    self.sendReply("({0}/{1}) {startStation} platform {startPlatform} at {2} 👉 {endStation} platform {endPlatform} at {3}".format(
                        currentSegment,
                        len(route['journey']),
                        track['startTime'].strftime("%H:%M"),
                        track['endTime'].strftime("%H:%M"),
                        **track
                    ))

            # Just the departure station?
            elif not 'departure' in self.memory:
                self.sendReply("Okay. From which station would you like to depart?")
                self.commitToMemory({'lastQuestion': ChatQuestions.DEPARTURE})

            # Just the destination station?
            elif not 'destination' in self.memory:
                self.sendReply("Alright, where would you like to go?")
                self.commitToMemory({'lastQuestion': ChatQuestions.ARRIVAL})

            # Or is it just the departure or arrival time we're lacking?
            elif not 'time' in self.memory:
                self.sendReply("Great! What time do you want to leave?")
                self.commitToMemory({'lastQuestion': ChatQuestions.TIME})

            return True


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
    ns.chatLoop()
