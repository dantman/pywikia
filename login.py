#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to log the robot in to a wiki account.

Suggestion is to make a special account to use for robot use only. Make
sure this robot account is well known on your home wikipedia before using.

Parameters:

   -user:XXXX   logs in with username XXXX

   -pass:XXXX   uses XXXX as password. Be careful if you use this
                parameter because your password will be shown on your
                screen.

   -all         try to log in on all sites where a username is defined in
                user-config.py.
                
   -force       when doing -all, ignores if the user is already loged in,
                and tries to login for all listed sites.
                This may be useful if you have changed the account name
                and need to aquire new login cookies.

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
        self.site = site or wikipedia.getSite()
        try:
            self.username = username or config.usernames[self.site.family.name][self.site.lang]
        except:
            wikipedia.output(u'ERROR: Username for %s:%s is undefined.\nIf you have an account for that site, please add such a line to user-config.py:\n\nusernames[\'%s\'][\'%s\'] = \'myUsername\'' % (self.site.family.name, self.site.lang, self.site.family.name, self.site.lang))
            sys.exit(1)
        self.password = password

    def botAllowed(self):
        """
        Checks whether the bot is listed on Wikipedia:Bots to comply with
        the policy on the English and the Simple English Wikipedia.
        """
        if self.site in (wikipedia.getSite('en', 'wikipedia'), wikipedia.getSite('simple', 'wikipedia')):
            pl = wikipedia.Page(self.site, "Wikipedia:Bots")
            text = pl.get()
            return "[[user:%s" % self.username.lower() in text.lower()
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

    def login(self, retry = False):
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
            wikipedia.output(u'*** Your username is not listed on [[Wikipedia:Bots]].\n*** Please make sure you are allowed to use the robot before actually using it!')
        cookiedata = self.getCookie()
        if cookiedata:
            self.storecookiedata(cookiedata)
            wikipedia.output(u"Should be logged in now")
            return True
        else:
            wikipedia.output(u"Login failed. Wrong password?")
            if retry:
                self.password = None
                return self.login(retry = True)
            else:
                return False

def main():
    username = password = None
    logall = False
    forceLogin = False
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'login')
        if arg:
            if arg.startswith("-user:"):
                username = arg[6:]
            elif arg.startswith("-pass:"):
                password = arg[6:]
            elif arg == "-all":
                logall = True
            elif arg == "-force":
                forceLogin = True
            else:
                wikipedia.showHelp('login')
                sys.exit()
    if logall:
        for familyName in config.usernames.iterkeys():
            for lang in config.usernames[familyName].iterkeys():
                site = wikipedia.getSite(code=lang, fam=familyName)
                if not forceLogin and site.loggedin():
                    wikipedia.output(u'Already logged in on %s' % site)
                else:
                    loginMan = LoginManager(username, password, site = site)
                    loginMan.login()
    else:
        loginMan = LoginManager(username, password)
        loginMan.login()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()