#!/usr/bin/python
"""
Script to perform some tests.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license
#
__version__='$Id$'
#
import re,sys,wikipedia

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        print "Unknown argument",arg
        sys.exit(1)

mysite = wikipedia.getSite()
if mysite.loggedin(check=1):
    print "Logged in (%s)" % repr(mysite)
else:
    print "Not logged in (%s)" % repr(mysite)
