#!/usr/bin/python
"""
Script to test whether you are logged-in

Parameters:

   -all         Try to test on all sites where a username is defined in
                user-config.py.
   -sysop       test your sysop account. (Works only with -all)
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#
import re,sys,wikipedia,config

def show (mysite):
    if mysite.loggedInAs():
        wikipedia.output(u"You are logged in on %s as %s." % (repr(mysite), mysite.loggedInAs()))
    else:
        wikipedia.output(u"You are not logged in on %s." % repr(mysite))

def main():
    testall = False
    sysop   = False
    for arg in wikipedia.handleArgs():
        if arg == "-all":
            testall = True
        elif arg == "-sysop":
            sysop = True
        else:
            wikipedia.showHelp()
            return
    if testall:
        if sysop:
            namedict = config.sysopnames
        else:
            namedict = config.usernames
        for familyName in namedict.iterkeys():
            for lang in namedict[familyName].iterkeys():
                 show(wikipedia.getSite(lang, familyName))
    else:
        show(wikipedia.getSite())

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
