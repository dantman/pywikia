"""
Loop over all pages in the home wikipedia, standardizing the interwiki links.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import os,sys

import wikipedia

options=[]
start=[]
file=[]
hints={}

debug = 0
forreal = 0

for arg in sys.argv[1:]:
    start.append(arg)

if start:
    start='_'.join(start)
else:
    start='0'

for pl in wikipedia.allpages(start = start):
    print pl
    try:
        oldtext = pl.get()
    except wikipedia.IsRedirectPage:
        print "--->is redirect"
        continue
    except wikipedia.LockedPage:
        print "--->is locked"
        continue
    old = pl.interwiki()
    new = {}
    for pl2 in old:
        new[pl2.code()] = pl2
    newtext = wikipedia.replaceLanguageLinks(oldtext, new)
    if newtext != oldtext:
        # Display the difference
        import difflib
        for line in difflib.ndiff(oldtext.split('\r\n'),newtext.split('\r\n')):
            if line[0] in ['+','-']:
                print repr(line)[2:-1]
        # Submit changes
        if forreal:
            status, reason, data = pl.put(newtext,
                                          comment='robot interwiki standardization')
            if str(status) != '302':
                print status, reason
        
