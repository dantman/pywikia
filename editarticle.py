#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distribute under the terms of the PSF license.

# Version 0.2.
#
# Features:
#       - logging in
#       - editing anonymously
#
# TODO: - non existing pages
#       - correct encoding
#       - use cookies to remember login
#       - redirect pages
#
#       - ...
#

__version__ = "$Id$"

import sys
import os
import httplib
## import cookielib
import getpass
import optparse
import tempfile

import wikipedia
import login

def options(args):
    parser = optparse.OptionParser()
    parser.add_option("-a", "--anonymous", action="store_true", default=False, help="Login anonymously")
    parser.add_option("-u", "--username", help="Username to login with (ignored with -a)")
    parser.add_option("-p", "--page", help="Page to edit")
    parser.add_option("-e", "--editor", help="Editor to use")
##    parser.add_option("-p", "--password", help="Password to login with")
    return parser.parse_args(args=args)

def editpage(pl, editor):
    """Edit a pagelink using an editor.
    
    Takes two arguments: page and editor.
    
    It returns two strings: the old version and the new version."""
    ofn = tempfile.mktemp()
    ofp = open(ofn, 'w')
    oldcontent = pl.get()
    ofp.write(oldcontent.encode('utf-8')) # FIXME: encoding of wiki
    ofp.close()
    os.system("%s %s" % (editor, ofn))
    newcontent = open(ofn).read().decode('utf-8')
    return oldcontent, newcontent

## def login(username, password):
##     """Login with username and password.
##     
##     Return cookie object on success, False otherwise"""
## 
##     data = {"wpName": username,
##             "wpPassword": password,
##             "wpLoginattempt": "Aanmelden & inschrijven",
##             "wpRemember": "0"} # FIXME: cookies
##     data = wikipedia.urlencode(data.items())
##     headers = {"Content-type": "application/x-www-form-urlencoded",
##                "User-agent": "editarticle.py $Revision$"}
##     mysite = wikipedia.getSite()
##     pagename = mysite.login_address()
##     conn = httplib.HTTPConnection(mysite.hostname())
##     conn.request("POST", pagename, data, headers, )
##     response = conn.getresponse()
##     cookie = response.getheader("set-cookie")
##     print cookie
##     if response.status == 302: # Moved temporarily
##         return cookie
##     else:
##         return False

def main():
    args = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            args.append(arg)
    opts, otherargs = options(args)
    if opts.anonymous:
        site = wikipedia.getSite()
    else:
        username = opts.username or raw_input("Username: ")
        site = wikipedia.getSite(user=opts.username)
        password = getpass.getpass("Password: ")
        cookie = login.login(site, username, password)
        if cookie:
            login.storecookiedata(cookie, site, username)
            print "Login succesful"
        else:
            sys.exit("Login failed")

    page = opts.page or raw_input("Page to edit: ")
    editor = opts.editor or raw_input("Editor to use: ")
    pl = wikipedia.PageLink(site, page)
    old, new = editpage(pl, editor)
    if old != new:
        pl.put(new, comment=raw_input("What did you change? "), anon=opts.anonymous)
    else:
        print "Nothing changed"


if __name__ == "__main__":
    main()
