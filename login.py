#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to log the robot in to a wikipedia account.

Suggestion is to make a special account to use for robot use only. Make
sure this robot account is well known on your home wikipedia before using.

This script has no command line arguments. Please run it as such. It will ask
for your username and password (it will show your password on the screen!), log
in to your home wikipedia using this combination, and store the resulting
cookies (containing your password in encoded form, so keep it secured!) in a
file named login.data

The wikipedia library will be looking for this file and will use the login
information if it is present.

Arguments:

  -lang:xx Log in to the given wikipedia language
  
To log out, throw away the XX-login.data file that is created in the login-data
subdirectory..
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

def allowedbot(site):
    """Checks whether the bot is listed on Wikipedia:bots"""
    pl = wikipedia.PageLink(site, "Wikipedia:Bots")
    text = pl.get()
    return "[[User:%s" % username in text

def login(site, username, password, remember=True):
    """Login to wikipedia.

    site        Site object for Wikipedia language+family
    username    Username to login with
    password    Password for username
    remember    Remember login (default: True)
    
    Returns cookie data if succesful, False otherwise."""

    data = {"wpName": username,
            "wpPassword": password,
            "wpLoginattempt": "Aanmelden & Inschrijven",
            "wpRemember": str(int(bool(remember)))}
    data = wikipedia.urlencode(data.items())
    headers = {"Content-type": "application/x-www-form-urlencoded", 
               "User-agent": "RobHooftWikiRobot/1.0"}
    pagename = site.login_address()
    conn = httplib.HTTPConnection(site.hostname())
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
        return False

def storecookiedata(data, site, user=None):
    """Stores cookie data
    
    The first argument is the raw data, as returned by login().
    The second argument is the Site object.
    The third argument is optional and is the user. It allows muliple-user bots.
    If it is not given, the filename is old-style. Otherwise, the username is
    also included in the filename for the login data.
    
    Returns nothing."""

    if user is None:
        user = ""
    else:
        user += "-"
    f = open(makepath('login-data/%s-%s-%slogin.data' % (site.family.name, site.lang, user)), 'w')
    f.write(data)
    f.close()

def main(args):

    username = password = None
    for arg in args:#sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg.startswith("-user:"):
            username = arg[6:]
        elif arg.startswith("-pass:"): # not recommended
            password = arg[6:]
        else:
            sys.exit("Unknown argument: %s" % arg)

    mysite = wikipedia.getSite()
    wikipedia.output(u"Logging in to %s" % repr(mysite))

    user = username
    if username is None:
        username = config.username # wikipedia.input(u'username:', encode = True)
    if not password:
        # As we don't want the password to appear on the screen, we use getpass(). 
        password = getpass.getpass('password: ')
    # Convert the password from the encoding your shell uses to the one your wiki
    # uses, via Unicode. This is the same as wikipedia.input() does with the 
    # username, but input() uses raw_input() instead of getpass().
    password = unicode(password, config.console_encoding)
    password = password.encode(wikipedia.myencoding())

    # Ensure bot policy on the English Wikipedia
    ensite=wikipedia.getSite(code='en',fam='wikipedia')
    if mysite == ensite:
        if not allowedbot(ensite):
            print "Your username is not listed on [[Wikipedia:Bots]]"
            print "Please make sure you are allowed to use the robot"
            print "Before actually using it!"
            
    cookiedata = login(mysite, username, password)
    print cookiedata
    if cookiedata:
        storecookiedata(cookiedata, mysite, user)
        print "Should be logged in now"
    else:
        print "Login failed. Wrong password?"

if __name__ == "__main__":
    main(sys.argv[1:])
