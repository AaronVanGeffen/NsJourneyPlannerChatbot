# NS Journey Planner Chatbot

A simple interactive shell chatbot that allows you to plan a journey with NS,
the Dutch Railways. Written in Python 3.

## Prerequisites

Our scripts do not depend on any packages outside of Python 3's base packages.
You will, however, need to [request an API key](https://www.ns.nl/ews-aanvraagformulier/)
for the NS API.

## Running the bot
```
$ ./clibot.py
usage: clibot.py [-h] -l LOGIN -p PASSWORD [-v]
```

We recommend to run clibot.py with its arguments through a simple shell script
for easy access.

## NS API

The NS API uses basic HTTP requests. Requests are done through simpele GET requests;
responses are XML and are therefore easy to process. More information on the API
can be found in its extensive documentation, which is available in both
[Dutch](http://www.ns.nl/reisinformatie/ns-api) and
[English](http://www.ns.nl/en/travel-information/ns-api).

## Features

Aside from exchanging basic pleasantries, the bot is able to give the user a full
journey advice, including transfers. This can either be done through interactive
dialogue, or by processing a full sentence.

**Brief example**
```
>>> Hello! I'd like to go to Amsterdam from Nijmegen at 18:00, please.
Hello there!
The next train to Amsterdam departs at 18:13 from station Nijmegen.
Planned travel time is 1:22.
(1/1) Nijmegen platform 4a at 18:13 👉 Amsterdam Centraal platform 8a at 19:35
```

**A more extensive example**
```
>>> Hi!
Hello there!

>>> I wanna go to Groningen Europapark!
Okay. From which station would you like to depart?

>>> Nijmegen Lent
Alright, departing at Nijmegen Lent.
Great! What time do you want to leave?

>>> 22:30
Alright, departing at 22:30
The next train to Groningen departs at 23:04 from station Nijmegen Lent.
You will have to transfer 3 times.
Planned travel time is 3:28.
(1/4) Nijmegen Lent platform 1 at 23:04 👉 Arnhem Centraal platform 3 at 23:19
(2/4) Arnhem Centraal platform 3 at 23:41 👉 Zwolle platform 10 at 00:41
(3/4) Zwolle platform 6a at 00:52 👉 Beilen platform 2 at 01:31
(4/4) Beilen platform None at 01:36 👉 Groningen platform None at 02:32

>>> Alright, thanks.
Oh, you're very welcome!

>>> Bye!
Bye bye! See you next time!
```

## Future work

The `NsBot` has been constructed in such a way that it can be used as a base class
for extensions, e.g. for it to function as a bot on an IRC or IM network. Due to
time constraints, we have not made such an implementation as of yet.

Currently, the bot is unable to tell the price of a journey, as the NS API
consistently returns an HTTP 403 error.
