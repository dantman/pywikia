#coding: iso-8859-1
"""
This bot takes its input from a file that contains a number of
pages to be put on the wiki. The pages should all have the same
begin and end text (which may not overlap), and should have the
intended title of the page as the first text in bold (that is,
between ''' and '''). The default is not to include the begin and
end text in the page, if you want to include that text, use
the -include option.

Specific arguments:
-start:xxx  Specify the text that is the beginning of a page
-end:xxx    Specify the text that is the end of a page
-file:xxx   Give the filename we are getting our material from
-include    The beginning and end text should be included in the
            page.
"""
#
# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#

import wikipedia
import re, sys

msg={
    'en':u'Automated import of articles',
    'nl':u'Geautomatiseerde import'
    }

# Adapt these to the file you are using. 'starttext' and 'endtext' are
# the beginning and end of each entry. Take text that should be included
# and does not occur elsewhere in the text.
starttext = "{{-scn-}}"
endtext = "{{-proofreading-}}"
filename = "dict.txt"
include = False

def findpage(t):
    try:
        location = re.search(starttext+"([^\Z]*?)"+endtext,t)
        if include:
            page = location.group()
        else:
            page = location.group(1)
    except AttributeError:
        return
    try:
        title = re.search("'''(.*?)'''",page).group(1)
        pl = wikipedia.PageLink(mysite,title)
        if pl.exists():
            print "Page %s already exists, not adding!"%title
        else:
            pl.put(page, comment = commenttext, minorEdit = False)
    except AttributeError:
        print "No title found - skipping a page."
    findpage(t[location.end()+1:])
    return

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if arg.startswith("-start:"):
            starttext=arg[7:]
        if arg.startswith("-stop:"):
            endtext=arg[6:]
        if arg.startswith("-file:"):
            filename=arg[6:]
        if arg=="-include":
            include = True
        else:
            print "Disregarding unknown argument %s."%arg

mysite = wikipedia.getSite()
commenttext = wikipedia.translate(mysite,msg)

text = []

f=open(filename)
for line in f.readlines():
    text.append(line)

text=''.join(text)

findpage(text)
    
