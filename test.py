#!/usr/bin/python
"""
Script to perform some tests.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#
import re,sys,wikipedia

def main():
    for arg in wikipedia.handleArgs():
    wikipedia.output(u"Unknown argument: %s" % arg)
    wikipedia.stopme()
    sys.exit(1)

    mysite = wikipedia.getSite()
    if mysite.loggedInAs():
    wikipedia.output(u"You are logged in on %s as %s." % (repr(mysite), mysite.loggedInAs()))
    else:
    wikipedia.output(u"You are not logged in on %s." % repr(mysite))

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
