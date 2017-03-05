#!/usr/bin/env python3
from NsApi import NsApi

API_LOGIN    = ""
API_PASSWORD = ""

class NsBot:
    def __init__(self, login, password):
        self.ns = NsApi(login, password)

        self.knownStations = self.ns.getStationsAsList()
        self.knownStations = [x.lower() for x in self.knownStations]



    def compareList(self, list1, list2):
        for value in list1:
            if value in list2:
                return True
        return False


    def chat(self):
        planningList = ["plan", "planning"]
        quitList = ["quit", "stop"]
        confirmList = ["yes", "yeah", "yep", "sure", "y"]
        denyList = ["no", "nope", "n"]

        print ("Hello! I am the NS-chatbot!")
        print ("How can I help you?")

        while True:
            userInput = input(">>> ")
            input_list = userInput.split()

            if self.compareList(input_list, planningList):
                print("From which station do you want to take the train?")
                departureStation = input(">>> ")
                if self.compareList(departureStation.lower().split(), self.knownStations):
                    print("Valid station")

                print("Where do you want to go?")
                arrivalStation = input(">>> ")
                if self.compareList(arrivalStation.lower().split(), self.knownStations):
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



        if ns.compareList(input_list, quitList):
                sys.exit("Goodbye!")


ns = NsBot(API_LOGIN, API_PASSWORD)
ns.chat()


#ns.getJourneyPrice("Nm", "Ut")
#departureTime, route = ns.getPossibleRoutes("Nm", "Ut")

#departureTime = route.find("GeplandeVertrekTijd")

