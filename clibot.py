#!/usr/bin/env python3
from NsApi import NsApi

API_LOGIN    = ""
API_PASSWORD = ""

ns = NsApi(API_LOGIN, API_PASSWORD)

stationList = ns.getStationsAsList()
stationList = [x.lower() for x in stationList]


planningList = ["plan", "planning"]

quitList = ["quit", "stop"]
confirmList = ["yes", "yeah", "yep", "sure", "y"]
denyList = ["no", "nope", "n"]

print ("Hello! I am the NS-chatbot!")
print ("How can I help you?")

while True:
        userInput = input(">>> ")
        input_list = userInput.split()

        if ns.compareList(input_list, planningList):

                print("From which station do you want to take the train?")
                departureStation = input(">>> ")
                if ns.compareList(departureStation.lower().split(), stationList):
                        print("Valid station")

                print("Where do you want to go?")
                arrivalStation = input(">>> ")
                if ns.compareList(arrivalStation.lower().split(), stationList):
                        print("Valid station")
                departureTime, travelTime = ns.getPossibleRoutes(departureStation, arrivalStation)
                departureTime = str(departureTime).split()
                print("The train from %s to %s leaves at: %s on: %s"% (departureStation, arrivalStation, departureTime[1][:-9], 
                                                                      departureTime[0])) 
                print("Would you like to know how long this trip is?")
                userInput = input(">>> ")
                if ns.compareList(userInput, confirmList):
                        print("The expected travel time is: %s" %travelTime)       

        if ns.compareList(input_list, quitList):
                sys.exit("Goodbye!")




#ns.getJourneyPrice("Nm", "Ut")
#departureTime, route = ns.getPossibleRoutes("Nm", "Ut")

#departureTime = route.find("GeplandeVertrekTijd")

