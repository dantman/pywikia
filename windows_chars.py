# -*- coding: utf-8 -*-
"""
Script to replace bad Windows-1252 (cp1252) characters with 
HTML entities on ISO 8859-1 wikis.

Syntax: python windows_chars.py [page_title] [file[:filename]]

Command line options:

   -file:XYZ  reads a list of pages, which can for example be gotten through 
              Looxix's robot. XYZ is the name of the file from which the
              list is taken. If XYZ is not given, the user is asked for a
              filename.
              Page titles should be saved one per line, without [[brackets]].

Options that are accepted by more robots:

    -lang:XX  set your home wikipedia to XX instead of the one given in
              username.dat



"""
#
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id: windows_chars.py,v 1.6 2004/07/13 12:26:00 wikipedian Exp $'
#
import wikipedia, config
import re, sys

# Summary message
msg={
    'en':'robot: changing Windows-1252 characters to HTML entities',
    'de':'Bot: Wandle Windows-1252-Zeichen in HTML-Entitäten um',
    }

# if the -file argument is used, page titles are dumped in this array.
# otherwise it will only contain one page.
page_list = []
# if -file is not used, this temporary array is used to read the page title.
page_title = []

for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-file'):
        if len(arg) == 5:
            file = wikipedia.input('Please enter the list\'s filename: ')
        else:
            file = arg[6:]
        # open file and read page titles out of it
        f=open(file)
        for line in f.readlines():
            if line != '\n':           
                page_list.append(line)
        f.close()
    else:
        page_title.append(arg)

# if the page is given as a command line argument,
# connect the title's parts with spaces
if page_title != []:
     page_title = ' '.join(page_title)
     page_list.append(page_title)

# if no page was given as an argument, and none was
# read from a file, query the user
if page_list == []:
    pagename = wikipedia.input('Which page to check: ', wikipedia.code2encoding(wikipedia.mylang))
    page_list.append(pagename)

# get edit summary message
msglang = wikipedia.chooselang(wikipedia.mylang,msg)
wikipedia.setAction(msg[msglang])

def treat(pl):
    try:
        reftxt=pl.get()
    except wikipedia.IsRedirectPage:
        pass
    except wikipedia.NoPage:
        print "Page not found: " + pl.linkname()
        pass
    else:
        count = 0
        for char in [u"\x80",         u"\x82", u"\x83", u"\x84", u"\x85", u"\x86", u"\x87", u"\x88", u"\x89", u"\x8A", u"\x8B", u"\x8C",      u"\x8E",
                             u"\x91", u"\x92", u"\x93", u"\x94", u"\x95", u"\x96", u"\x97", u"\x98", u"\x99", u"\x9A", u"\x9B", u"\x9C",      u"\x9E", u"\x9F"]:
            count += reftxt.count(char)
        
        print str(count) + " Windows-1252 characters were found."
        if count == 0:
            print "No changes required."
        else:
            reftxt = reftxt.replace(u"\x80", "&euro;")   # euro sign
            reftxt = reftxt.replace(u"\x82", "&sbquo")   # single low-9 quotation mark
            reftxt = reftxt.replace(u"\x83", "&fnof;")   # latin small f with hook = function = florin
            reftxt = reftxt.replace(u"\x84", "&bdquo;")  # double low-9 quotation mark
            reftxt = reftxt.replace(u"\x85", "&hellip;") # horizontal ellipsis = three dot leader
            reftxt = reftxt.replace(u"\x86", "&dagger;") # dagger
            reftxt = reftxt.replace(u"\x87", "&Dagger;") # double dagger
            reftxt = reftxt.replace(u"\x88", "&circ;")   # modifier letter circumflex accent
            reftxt = reftxt.replace(u"\x89", "&permil;") # per mille sign
            reftxt = reftxt.replace(u"\x8A", "&Scaron;") # latin capital letter S with caron
            reftxt = reftxt.replace(u"\x8B", "&#8249;")  # single left-pointing angle quotation mark
            reftxt = reftxt.replace(u"\x8C", "&OElig;")  # latin capital ligature OE
            reftxt = reftxt.replace(u"\x8E", "&#381;")   # latin capital letter Z with caron
            reftxt = reftxt.replace(u"\x91", "&lsquo;")  # left single quotation mark
            reftxt = reftxt.replace(u"\x92", "&rsquo;")  # right single quotation mark
            reftxt = reftxt.replace(u"\x93", "&ldquo;")  # left double quotation mark
            reftxt = reftxt.replace(u"\x94", "&rdquo;")  # right double quotation mark
            reftxt = reftxt.replace(u"\x95", "&bull;")   # bullet = black small circle
            reftxt = reftxt.replace(u"\x96", "&ndash;")  # en dash
            reftxt = reftxt.replace(u"\x97", "&mdash;")  # em dash
            reftxt = reftxt.replace(u"\x98", "&tilde;")  # small tilde
            reftxt = reftxt.replace(u"\x99", "&trade;")  # trade mark sign
            reftxt = reftxt.replace(u"\x9A", "&scaron;") # latin small letter s with caron
            reftxt = reftxt.replace(u"\x9B", "&8250;")   # single right-pointing angle quotation mark
            reftxt = reftxt.replace(u"\x9C", "&oelig;")  # latin small ligature oe
            reftxt = reftxt.replace(u"\x9E", "&#382;")   # latin small letter z with caron
            reftxt = reftxt.replace(u"\x9F", "&Yuml;")   # latin capital letter Y with diaeresis
            pl.put(reftxt)

if wikipedia.code2encoding(wikipedia.mylang) == "utf-8":
    print "There is no need to run this robot on UTF-8 wikis."
else:
    # loop over all given pages
    for page in page_list:
        pl=wikipedia.PageLink(wikipedia.mylang, page)
        treat(pl)
