"""
Script to correct URLs like
(http://www.example.org) to [http://www.example.org example.org]
to have correct generation of links in Wikipedia
"""

# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
__version__='$Id$'

import re,sys,wikipedia

mylang = "de"
myComment = 'Bot: URL fixed'

for arg in sys.argv[1:]:
    text= wikipedia.getPage(mylang, arg)

    newText = re.sub("\((http:\/\/([^ ]*))\)", "([\\1 \\2])", text)
    if newText!=text:
       status,reason,data = wikipedia.putPage(mylang, arg ,newText, myComment)
       print status,reason
    else:
       print "No bad link found"
