"""
Script to correct URLs like
(http://www.example.org) to [http://www.example.org example.org]
to have correct generation of links in Wikipedia
"""
#
# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import re, sys

import wikipedia

myComment = {'en':'Bot: URL fixed'
             }

try:
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        else:
            pl = wikipedia.PageLink(wikipedia.getSite(), arg)
            text = pl.get()
        
            newText = re.sub("(http:\/\/([^ ]*[^\] ]))\)", "[\\1 \\2])", text)

            if newText != text:
                wikipedia.showDiff(text, newText)
                status, reason, data = pl.put(newText, wikipedia.translate(wikipedia.mylang,myComment))
                print status, reason
            else:
                print "No bad link found"
except:
    wikipedia.stopme()
    raise

wikipedia.stopme()
