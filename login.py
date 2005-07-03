#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to log the robot in to a wiki account.

Suggestion is to make a special account to use for robot use only. Make
sure this robot account is well known on your home wikipedia before using.

Parameters:

   -user:XXXX   logs in with username XXXX

   -pass:XXXX   uses XXXX as password. It's not recommended to use this
                parameter because your password will be shown on your
                screen.

    
    
If not given as parameter, the script will ask for your username and password
(password entry will be hidden), log in to your home wiki using this
combination, and store the resulting cookies (containing your password hash,
so keep it secured!) in a file in the login-data subdirectory.

All bots in this library will be looking for this cookie file and will use the
login information if it is present.

To log out, throw away the XX-login.data file that is created in the login-data
subdirectory.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distributed under the terms of the PSF license.
#
__version__='$Id$'

import re, sys, getpass
import httplib
import wikipedia, config

def makepath(path):
    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18
    """
    from os import makedirs
    from os.path import normpath,dirname,exists,abspath

    dpath = normpath(dirname(path))
    if not exists(dpath): makedirs(dpath)
    return normpath(abspath(path))

class LoginManager:
    def __init__(self, username = None, password = None, site = None):
        self.username = username or config.username
        self.password = password
        self.site = site or wikipedia.getSite()

    def botAllowed(self):
        """
        Checks whether the bot is listed on Wikipedia:Bots to comply with
        the policy on the English Wikipedia.
        """
        if self.site == wikipedia.getSite('en', 'wikipedia'):
            pl = wikipedia.Page(self.site, "Wikipedia:Bots")
            text = pl.get()
            return "[[user:%s" % username.lower() in text.lower()
        else:
            # No bot policies on other 
            return True
    
    def getCookie(self, remember=True):
        """Login to wikipedia.
    
        remember    Remember login (default: True)
        
        Returns cookie data if succesful, None otherwise."""
    
        data = {"wpName": self.username,
                "wpPassword": self.password,
                "wpLoginattempt": "Aanmelden & Inschrijven", # dutch button label seems to work for all wikis
                "wpRemember": str(int(bool(remember)))}
        data = wikipedia.urlencode(data.items())
        headers = {
            "Content-type": "application/x-www-form-urlencoded", 
            "User-agent": "RobHooftWikiRobot/1.0"
        }
        pagename = self.site.login_address()
        conn = httplib.HTTPConnection(self.site.hostname())
        conn.request("POST", pagename, data, headers)
        response = conn.getresponse()
        conn.close()
        data = response.read()
    
        n=0
        Reat=re.compile(': (.*?);')
        L = []
        for eat in response.msg.getallmatchingheaders('set-cookie'):
            m = Reat.search(eat)
            if m:
                n += 1
                L.append(m.group(1))

        if len(L) == 4:
            return "\n".join(L)
        else:
            return None

    def storecookiedata(self, data):
        """
        Stores cookie data.

        The argument data is the raw data, as returned by getCookie().

        Returns nothing."""
        filename = 'login-data/%s-%s-login.data' % (self.site.family.name, self.site.lang)
        f = open(makepath(filename), 'w')
        f.write(data)
        f.close()

    def login(self):
        if not self.password:
            # As we don't want the password to appear on the screen, we use getpass(). 
            self.password = getpass.getpass('Password for user %s on %s: ' % (self.username, self.site))
            # Convert the password from the encoding your shell uses to the one your wiki
            # uses, via Unicode. This is the same as wikipedia.input() does with the 
            # username, but input() uses raw_input() instead of getpass().
            self.password = unicode(self.password, config.console_encoding)
    
        self.password = self.password.encode(wikipedia.myencoding())
    
        wikipedia.output(u"Logging in to %s as %s" % (self.site, self.username))
        # Ensure bot policy on the English Wikipedia
        if not self.botAllowed():
            wikipedia.output(u'Your username is not listed on [[Wikipedia:Bots]]. Please make sure you are allowed to use the robot before actually using it!')
        cookiedata = self.getCookie()
        if cookiedata:
            self.storecookiedata(cookiedata)
            wikipedia.output(u"Should be logged in now")
        else:
            wikipedia.output(u"Login failed. Wrong password?")

def main():
    username = password = None
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'login')
        if arg:
            if arg.startswith("-user:"):
                username = arg[6:]
            elif arg.startswith("-pass:"): # not recommended
                password = arg[6:]
            else:
                wikipedia.showHelp('login')
                sys.exit()
    loginMan = LoginManager(username, password)
    loginMan.login()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

