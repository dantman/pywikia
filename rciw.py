#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
A simple IRC script to check for Recent Changes through IRC,
and to check for interwikis in those recently modified articles.

In use on hu:, not sure if this scales well on a large wiki such
as en: (Depending on the edit rate, the number of IW threads
could grow continuously without ever decreasing)
"""

# Author: Kisbes
# http://hu.wikipedia.org/wiki/User:Kisbes
# License : GFDL

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
import interwiki
import threading
import re
import wikipedia
import time
from Queue import Queue

class SignerBot(SingleServerIRCBot):
    def __init__(self, site, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.other_ns = re.compile(u'14\[\[07(' + u'|'.join(site.namespaces()) + u')')
        interwiki.globalvar.autonomous = True
        self.site = site
        self.queue = Queue()
        # Start 20 threads
        for i in range(20):
            t = threading.Thread(target=self.worker)
            t.start()

    def worker(self):
        bot = interwiki.InterwikiBot()
        while True:
            # Will wait until one page is available
            bot.add(self.queue.get())
            bot.queryStep()
            self.queue.task_done()

    def join(self):
        self.queue.join()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
	pass

    def on_pubmsg(self, c, e):
        msg = unicode(e.arguments()[0],'utf-8')
        if not self.other_ns.match(msg):
            name = msg[8:msg.find(u'14',9)]
            page = wikipedia.Page(self.site, name)
            # the Queue has for now an (theoric) unlimited size,
            # it is a simple atomic append(), no need to acquire a semaphore
            self.queue.put_nowait(page)

    def on_dccmsg(self, c, e):
	pass

    def on_dccchat(self, c, e):
	pass

    def do_command(self, e, cmd):
	pass

    def on_quit(self, e, cmd):
	pass

def main():
    site = wikipedia.getSite()
    site.forceLogin()
    chan = '#' + site.language() + '.' + site.family.name
    bot = SignerBot(site, chan, site.loggedInAs(), "irc.wikimedia.org", 6667)
    try:
        bot.start()
    except:
        # Quit IRC
        bot.disconnect()
        # Join the IW threads
        bot.join()
        raise

if __name__ == "__main__":
    main()
