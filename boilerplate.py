# -*- coding: utf-8 -*-
"""
Very simple script to replace a MediaWiki boilerplate text with another one,
and to convert the old boilerplate format to the new one.

Syntax: python boilerplate.py [-newformat] oldBoilerplate [newBoilerplate]

Specify the MediaWiki boilerplate on the command line. The program will
pick up the boilerplate page, and look for all pages using it. It will
then automatically loop over them, and replace the boilerplate text.

Command line options:

-oldformat:   Use the old format {{msg:Stub}} instead of {{Stub}}.
              
other:        First argument is the old boilerplate name, second one is the new
              name. If only one argument is given, the bot resolves the
              boilerplate by putting its text directly into the article.
              This is done by changing {{...}} or {{msg:...}} into {{subst:...}}
"""
#
# (C) Daniel Herding, 2004
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia, config
import re, sys, string

# Summary message
msg={
    'en':u'Robot: Changing boilerplate text',
    'de':u'Bot: Ändere Textbaustein',
    }

def getReferences(pl):
    x = wikipedia.getReferences(pl)
    return x

oldformat = False
boilerplate_names = []
resolve = False
# read command line parameters
for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-oldformat':
        oldformat = True
    else:
        boilerplate_names.append(arg)

if boilerplate_names == []:
    print "Syntax: python boilerplate.py [-oldformat] oldBoilerplate [newBoilerplate]"
    sys.exit()
old = boilerplate_names[0]
if len(boilerplate_names) >= 2:
    new = boilerplate_names[1]
else:
    # if only one argument is given, don't replace the boilerplate with another
    # one, but resolve the boilerplate by putting its text directly into the
    # article.
    resolve = True

# get edit summary message
wikipedia.setAction(msg[wikipedia.chooselang(wikipedia.mylang,msg)]+': '+old)

# get template namespace
ns = wikipedia.family.template[wikipedia.mylang]
# Download 'What links here' of the boilerplate
thispl = wikipedia.PageLink(wikipedia.mylang, ns + ':' + old)

def treat(refpl):
    try:
        reftxt=refpl.get()
    except wikipedia.IsRedirectPage:
        pass
    else:
        # Check if boilerplate is really used in this article
        if not boilerplateR.search(reftxt):
            print "Not found in %s"%refpl
            return
        
        # Replace all occurences of the boilerplate in this article
        if resolve:
            reftxt = re.sub(boilerplateR, '{{subst:' + old + '}}', reftxt)
        elif oldformat:
            reftxt = re.sub(boilerplateR, '{{msg:' + new + '}}', reftxt)
        else:
            reftxt = re.sub(boilerplateR, '{{' + new + '}}', reftxt)

        refpl.put(reftxt)

# regular expression to find the original boilerplate text.
# {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
# The new syntax, {{vfd}}, will also be found.
boilerplateR=re.compile(r'\{\{([mM][sS][gG]:)?[' + old[0].upper() + old[0].lower() + ']' + old[1:] + '}}')

# loop over all pages using the boilerplate
for ref in getReferences(thispl):
    refpl=wikipedia.PageLink(wikipedia.mylang, ref)
    treat(refpl)
