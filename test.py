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
                
if wikipedia.checkLogin():
    print "Logged in ("+wikipedia.mylang+".wikipedia.org)"
else:
    print "Not logged in ("+wikipedia.mylang+".wikipedia.org)"
