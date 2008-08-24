#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
A wiki-maintainer script that shares tasks between workers, requires no intervention.

Note: the script requires the Python IRC library http://python-irclib.sourceforge.net/
"""
__version__ = '$Id$'

# Author: Balasyum
# http://hu.wikipedia.org/wiki/User:Balasyum
# License : LGPL

from ircbot import SingleServerIRCBot
from irclib import nm_to_n
import random
import wikipedia
import threading
import time
import rciw

ver = 1

class MaintcontBot(SingleServerIRCBot):
    def __init__(self, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.rct = threading.Thread(target=rciw.main)
        self.rct.setDaemon(True)
        self.rciwrunning = False

    def on_nicknameinuse(self, c, e):
        c.nick("mainter" + str(random.randrange(100, 999)))

    def on_welcome(self, c, e):
        site = wikipedia.getSite()
        site.forceLogin()
        self.connection.privmsg("maintcont", "workerjoin " + site.language() + '.' + site.family.name + ' ' + str(ver))

    def on_privmsg(self, c, e):
        nick = nm_to_n(e.source())
        c = self.connection
        cmd = e.arguments()[0]
        do = cmd.split()
        if do[0] == "accepted":
            print "Joined the network"
            t = threading.Thread(target=self.activator)
            t.setDaemon(True)
            t.start()
        elif do[0] == "tasklist" and len(do) > 1:
            tasks = do[1].split('|')
            if 'rciw' in do[1]:
                self.rct.start()
                self.rciwrunning = True
            if (not 'rciw' in do[1]) and self.rciwrunning:
                self.rct.join(0)
                self.rciwrunning = False

    def on_dccmsg(self, c, e):
        pass

    def on_dccchat(self, c, e):
        pass

    def activator(self):
        while True:
            self.connection.privmsg("maintcont", "active")
            time.sleep(10)

def main():
    bot = MaintcontBot("mainter" + str(random.randrange(100, 999)), "irc.freenode.net")
    bot.start()

if __name__ == "__main__":
    main()