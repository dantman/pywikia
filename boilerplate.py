# -*- coding: utf-8 -*-
"""
Very simple script to replace a template with another one,
and to convert the old MediaWiki boilerplate format to the new template format.

Syntax: python boilerplate.py [-newformat] oldBoilerplate [newBoilerplate]

Specify the template on the command line. The program will
pick up the template page, and look for all pages using it. It will
then automatically loop over them, and replace the template.

Command line options:

-oldformat:   Use the old format {{msg:Stub}} instead of {{Stub}}.

-remove:      Remove every occurence of the template from every article

other:        First argument is the old template name, second one is the new
              name. If only one argument is given, the bot resolves the
              template by putting its text directly into the article.
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

# Summary messages
msg_change={
    'en':u'Robot: Changing template: %s',
    'de':u'Bot: Ändere Vorlage: %s',
    }

msg_remove={
    'en':u'Robot: Removing template: %s',
    'de':u'Bot: Entferne Vorlage: %s',
    }
    
def getReferences(pl):
    x = wikipedia.getReferences(pl)
    return x

oldformat = False
boilerplate_names = []
resolve = False
remove = False
# read command line parameters
for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-remove':
        remove = True
    elif arg == '-oldformat':
        oldformat = True
    else:
        boilerplate_names.append(arg)

if boilerplate_names == []:
    print "Syntax: python boilerplate.py [-oldformat] [-remove] oldBoilerplate [newBoilerplate]"
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
if remove:
    wikipedia.setAction(msg_remove[wikipedia.chooselang(wikipedia.mylang, msg_remove)] % old)
else:
    wikipedia.setAction(msg_change[wikipedia.chooselang(wikipedia.mylang, msg_change)] % old)
    

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
        if remove:
            reftxt = re.sub(boilerplateR, '', reftxt)
        elif resolve:
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
