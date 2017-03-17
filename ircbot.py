#!/usr/bin/env python3

import argparse

from clibot import NsBot
from dazeus import DaZeus


class DaZeusNS(NsBot):
    doBasicPleasantries = False

    def __init__(self, login, password, address, verbose = False):
        self.dazeus = DaZeus(address, verbose)
        self.dazeus.subscribe_command("ns", self.handleIRCmessage)
        super().__init__(login, password, verbose)

    def handleIRCmessage(self, event, reply):
        # TODO: this can go wrong (race conditions)
        self.reply = reply
        self.handleMessage(event['params'][4])

    def sendReply(self, msg):
        self.reply(msg)

    def chatLoop(self):
        self.resetMemory()
        self.dazeus.listen()


# Optionally run the bot.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'DaZeus plugin for Dutch Railways planner bot.', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-a', '--address', required = True, help='Address of the DaZeus instance to connect to. ' +
        'Use either `unix:/path/to/file` or `tcp:host:port`.')
    parser.add_argument('-l', '--login', required = True, help = 'your API account email address')
    parser.add_argument('-p', '--password', required = True, help = 'your API account password')
    parser.add_argument('-v', '--verbose', default = False, help = "increase output verbosity", action = "store_true")

    # Fetch command line arguments.
    args = parser.parse_args()

    # Run the bot.
    ns = DaZeusNS(args.login, args.password, args.address, args.verbose)
    ns.chatLoop()
