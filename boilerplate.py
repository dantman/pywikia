# -*- coding: cp1252 -*-
"""
Very simple script to replace a MediaWiki boilerplate text with another one,
and to convert the old boilerplate format to the new one.

Syntax: python boilerplate.py [-newformat] oldBoilerplate [newBoilerplate]

Specify the MediaWiki boilerplate on the command line. The program will
pick up the boilerplate page, and look for all pages using it. It will
then automatically loop over them, and replace the boilerplate text.

Command line options:

-newformat:   Use the new format {{stub}} instead of {{msg:stub}}.
              Note: we might want to change this to -oldformat and make the
              new format the default later.
other:        First argument is the old boilerplate name, second one is the new
              name. If only one argument is given, the bot resolves the
              boilerplate by putting its text directly into the article.
              This is done by changing msg: into subst:.
"""
#
# (C) Daniel Herding, 2004
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia,re,sys,string

# Summary message
msg={
    'en':'Robot: Changing boilerplate text',
    'de':'Bot: \xc4ndere Textbaustein',
    }

def getReferences(pl):
    x = wikipedia.getReferences(pl)
    return x

oldformat = True
boilerplate_names = []
resolve = False
# read command line parameters
for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-newformat':
        oldformat = False
    else:
        boilerplate_names.append(arg)

if boilerplate_names == []:
    print "Syntax: python boilerplate.py [-newformat] oldBoilerplate [newBoilerplate]"
    # Bug: this exit thingy doesn't work.
    sys.exit
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

# Download 'What links here' of the boilerplate
thispl = wikipedia.PageLink(wikipedia.mylang, 'MediaWiki:' + old)


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
            reftxt = re.sub(boilerplateR, '{{subst:' + unicode(old, 'iso-8859-1') + '}}', reftxt)
        elif oldformat:
            reftxt = re.sub(boilerplateR, '{{msg:' + unicode(new, 'iso-8859-1') + '}}', reftxt)
        else:
            reftxt = re.sub(boilerplateR, '{{' + unicode(new, 'iso-8859-1') + '}}', reftxt)

        refpl.put(reftxt)

# regular expression to find the original boilerplate text.
# {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
# The new syntax, {{vfd}}, will also be found.
boilerplateR=re.compile(r'\{\{([mM][sS][gG]:)?[' + old[0].upper() + old[0].lower() + ']' + old[1:] + '}}')

# loop over all pages using the boilerplate
for ref in getReferences(thispl):
    refpl=wikipedia.PageLink(wikipedia.mylang, ref)
    treat(refpl)
