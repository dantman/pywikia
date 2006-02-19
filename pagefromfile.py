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
# Distributed under the terms of the MIT license.
#

__version__='$Id:'

import wikipedia, config
import re, sys, codecs

msg={
    'de': u'Automatischer Import von Artikeln',
    'en': u'Automated import of articles',
    'ia': u'Importation automatic de articulos',
    'nl': u'Geautomatiseerde import'
    }

# Adapt these to the file you are using. 'starttext' and 'endtext' are
# the beginning and end of each entry. Take text that should be included
# and does not occur elsewhere in the text.
# TODO: Why not use the entire file contents?
starttext = "{{-start-}}"
endtext = "{{-stop-}}"
filename = "dict.txt"
include = False

def findpage(t):
    try:
        location = re.search(starttext+"([^\Z]*?)"+endtext,t)
        if include:
            contents = location.group()
        else:
            contents = location.group(1)
    except AttributeError:
        print 'Start or end marker not found.'
        return
    try:
        title = re.search("'''(.*?)'''", contents).group(1)
    except AttributeError:
        wikipedia.output(u"No title found - skipping a page.")
        return
    else:
        page = wikipedia.Page(mysite, title)
        wikipedia.output(page.title())
        if page.exists():
            wikipedia.output(u"Page %s already exists, not adding!"%title)
        else:
            page.put(contents, comment = commenttext, minorEdit = False)
    findpage(t[location.end()+1:])
    return

def main():
    text = []
    f = codecs.open(filename,'r', encoding = config.textfile_encoding)
    text = f.read()
    findpage(text)

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg, 'pagefromfile')
    if arg:
        if arg.startswith("-start:"):
            starttext=arg[7:]
        elif arg.startswith("-end:"):
            endtext=arg[5:]
        elif arg.startswith("-file:"):
            filename=arg[6:]
        elif arg=="-include":
            include = True
        else:
            wikipedia.output(u"Disregarding unknown argument %s."%arg)
mysite = wikipedia.getSite()
commenttext = wikipedia.translate(mysite,msg)

try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()

