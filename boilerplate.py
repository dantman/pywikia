# -*- coding: cp1252 -*-
"""
Very simple script to replace a MediaWiki boilerplate text with another one.

Syntax: python boilerplate.py oldBoilerplate newBoilerplate

Specify the MediaWiki boilerplate on the command line. The program will
pick up the boilerplate page, and look for all pages using it. It will
then automatically loop over them, and replace the boilerplate text.

Command line options:

none yet, except for the boilerplates
             
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

if not wikipedia.special.has_key(wikipedia.mylang):
    print "Please add the translation for the Special: namespace in"
    print "Your home wikipedia to the wikipedia.py module"
    import sys
    sys.exit(1)

# Summary message
msg={
    'en':'Robot: Changing boilerplate text',
    'de':'Bot: \xc4ndere Textbaustein',
    }


def getReferences(pl):
    x = wikipedia.getReferences(pl)
    return x

# read command line parameters
old = sys.argv[1]
new = sys.argv[2]

# get edit summary message
if msg.has_key(wikipedia.mylang):
    msglang = wikipedia.mylang
else:
    msglang = 'en'

wikipedia.setAction(msg[msglang]+': '+old)

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
        reftxt = re.sub(boilerplateR, '{{msg:' + unicode(new, 'iso-8859-1') + '}}', reftxt)

        print "Changing page %s" %(refpl)
        refpl.put(reftxt)
    
# regular expression to find the original boilerplate text.
# {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
boilerplateR=re.compile(r'\{\{[mM][sS][gG]:[' + old[0].upper() + old[0].lower() + ']' + old[1:] + '}}')

# loop over all pages using the boilerplate
for ref in getReferences(thispl):
    refpl=wikipedia.PageLink(wikipedia.mylang, ref)
    treat(refpl)

