# -*- coding: utf-8 -*-
"""
Very simple script to replace a template with another one,
and to convert the old MediaWiki boilerplate format to the new template format.

Syntax: python boilerplate.py [-newformat] oldTemplate [newTemplate]

Specify the template on the command line. The program will
pick up the template page, and look for all pages using it. It will
then automatically loop over them, and replace the template.

Command line options:

-oldformat - Use the old format {{msg:Stub}} instead of {{Stub}}.

-remove    - Remove every occurence of the template from every article

-sql       - retrieve information from a local dump (http://download.wikimedia.org).
             if this argument isn\'t given, info will be loaded from the maintenance
             page of the live wiki.
             argument can also be given as "-sql:filename.sql".

other:       First argument is the old template name, second one is the new
             name. If only one argument is given, the bot resolves the
             template by putting its text directly into the article.
             This is done by changing {{...}} or {{msg:...}} into {{subst:...}}
             
             If you want to address a template which has spaces, put quotation
             marks around it.
             
Example:

If you have a template called [[Template:Cities in Washington]] and want to
change it to [[Template:Cities in Washington state]], start

    python boilerplate.py "Cities in Washington" "Cities in Washington state"

Move the page [[Template:Cities in Washington]] manually afterwards.
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

def treat(refpl):
    try:
        reftxt=refpl.get()
    except wikipedia.IsRedirectPage:
        pass
    else:
        # Check if template is really used in this article
        if not templateR.search(reftxt):
            print "Not found in %s"%refpl
            return
        
        # Replace all occurences of the template in this article
        if remove:
            reftxt = re.sub(templateR, '', reftxt)
        elif resolve:
            reftxt = re.sub(templateR, '{{subst:' + old + '}}', reftxt)
        elif oldformat:
            reftxt = re.sub(templateR, '{{msg:' + new + '}}', reftxt)
        else:
            reftxt = re.sub(templateR, '{{' + new + '}}', reftxt)

        refpl.put(reftxt)
    
def getReferences(pl):
    x = wikipedia.getReferences(pl)
    return x

oldformat = False
template_names = []
resolve = False
remove = False
# If sqlfilename is None, references will be loaded from the live wiki.
sqlfilename = None
# read command line parameters
for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-remove':
        remove = True
    elif arg == '-oldformat':
        oldformat = True
    elif arg.startswith('-sql'):
        if len(arg) == 4:
            sqlfilename = wikipedia.input('Please enter the SQL dump\'s filename: ')
        else:
            sqlfilename = arg[5:]
    else:
        template_names.append(arg)

if template_names == []:
    print "Syntax: python boilerplate.py [-oldformat] [-remove] oldTemplate [newTemplate]"
    sys.exit()
old = template_names[0]
if len(template_names) >= 2:
    new = template_names[1]
else:
    # if only one argument is given, don't replace the template with another
    # one, but resolve the template by putting its text directly into the
    # article.
    resolve = True

# get edit summary message
if remove:
    wikipedia.setAction(msg_remove[wikipedia.chooselang(wikipedia.mylang, msg_remove)] % old)
else:
    wikipedia.setAction(msg_change[wikipedia.chooselang(wikipedia.mylang, msg_change)] % old)
    

# get template namespace
ns = wikipedia.family.template[wikipedia.mylang]
# Download 'What links here' of the template page
thispl = wikipedia.PageLink(wikipedia.mylang, ns + ':' + old)


# regular expression to find the original template.
# {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
# The new syntax, {{vfd}}, will also be found.
templateR=re.compile(r'\{\{([mM][sS][gG]:)?[' + old[0].upper() + old[0].lower() + ']' + old[1:] + '}}')

# loop over all pages using the template
if sqlfilename == None:
    for ref in getReferences(thispl):
        refpl=wikipedia.PageLink(wikipedia.mylang, ref)
        treat(refpl)
        print ''
else:
    import sqldump
    dump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())
    for entry in dump.entries():
        if templateR.search(entry.text):
            pl=wikipedia.PageLink(wikipedia.mylang, entry.full_title())
            treat(pl)
            print ''
