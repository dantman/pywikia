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
-utf        The input file is UTF-8

Note the '-utf' option is necessary on older versions of Windows;
whether it's necessary or useful on Windows XP and/or other
operating systems is unclear.
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
    'nl':u'Geautomatiseerde import',
    'pt':u'Importa�o autom�ica de artigo'
    }

# Adapt these to the file you are using. 'starttext' and 'endtext' are
# the beginning and end of each entry. Take text that should be included
# and does not occur elsewhere in the text.
starttext = "{{-scn-}}"
endtext = "{{-proofreading-}}"
filename = "dict.txt"
include = False
utf = False

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
        pl = wikipedia.Page(mysite,wikipedia.UnicodeToAsciiHtml(title))
        print pl.title()
        if pl.exists():
            print "Page %s already exists, not adding!"%title
        else:
            pl.put(page, comment = commenttext, minorEdit = False)
    except AttributeError:
        print "No title found - skipping a page."
    findpage(t[location.end()+1:])
    return

def main():
    text = []
    if utf:
        f=codecs.open(filename,'rb',encoding='utf-8')
    else:
        f=open(filename,'r')
    for line in f.readlines():
        text.append(line)
    text=''.join(text)
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
        elif arg=="-utf":
            import codecs
            utf = True
        else:
            print "Disregarding unknown argument %s."%arg
mysite = wikipedia.getSite()
commenttext = wikipedia.translate(mysite,msg)

try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()

