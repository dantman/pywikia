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

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg, 'test')
    if arg:
        print "Unknown argument",arg
        wikipedia.stopme()
        sys.exit(1)

mysite = wikipedia.getSite()
if mysite.loggedin():
    print "Logged in (%s)" % repr(mysite)
else:
    print "Not logged in (%s)" % repr(mysite)

wikipedia.stopme()
