# -*- coding: utf-8 -*-
"""
Very simple script to replace a template with another one,
and to convert the old MediaWiki boilerplate format to the new template format.

Syntax: python template.py [-newformat] oldTemplate [newTemplate]

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

    python template.py "Cities in Washington" "Cities in Washington state"

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

class TemplatePageGenerator:
    def __init__(self, templateName, sqlfilename = None):
        self.templateName = templateName
        self.sqlfilename = sqlfilename
        mysite = wikipedia.getSite()
    
        # get template namespace
        ns = mysite.template_namespace(fallback = None)
        # Download 'What links here' of the template page
        self.templatePl = wikipedia.PageLink(mysite, ns + ':' + templateName)
        # regular expression to find the original template.
        # {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
        # The new syntax, {{vfd}}, will also be found.
        self.templateR=re.compile(r'\{\{([mM][sS][gG]:)?[' + templateName[0].upper() + templateName[0].lower() + ']' + templateName[1:] + '}}')

    def generate(self):
        # yield all pages using the template
        if self.sqlfilename == None:
            for ref in wikipedia.getReferences(self.templatePl):
                refpl=wikipedia.PageLink(wikipedia.getSite(), ref)
                yield refpl
        else:
            import sqldump
            dump = sqldump.SQLdump(self.sqlfilename, mysite.encoding())
            for entry in dump.entries():
                if self.templateR.search(entry.text):
                    pl = wikipedia.PageLink(mysite, entry.full_title())
                    yield pl

class TemplateRobot:
    # Summary messages
    msg_change={
        'en':u'Robot: Changing template: %s',
        'de':u'Bot: Ändere Vorlage: %s',
        }
    
    msg_remove={
        'en':u'Robot: Removing template: %s',
        'de':u'Bot: Entferne Vorlage: %s',
        }

    def __init__(self, generator, old, new = None, remove = False, oldFormat = False):
        self.generator = generator
        self.old = old
        self.new = new
        self.remove = remove
        self.oldFormat = oldFormat
        # regular expression to find the original template.
        # {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
        # The new syntax, {{vfd}}, will also be found.
        self.templateR=re.compile(r'\{\{([mM][sS][gG]:)?[' + old[0].upper() + old[0].lower() + ']' + old[1:] + '}}')
        # if only one argument is given, don't replace the template with another
        # one, but resolve the template by putting its text directly into the
        # article.
        self.resolve = (new == None)
        # get edit summary message
        mysite = wikipedia.getSite()
        if self.remove:
            wikipedia.setAction(wikipedia.translate(mysite, self.msg_remove) % old)
        else:
            wikipedia.setAction(wikipedia.translate(mysite, self.msg_change) % old)

    def run(self):
        for pl in self.generator.generate():
            self.treat(pl)
    
    def treat(self, refpl):
        try:
            reftxt=refpl.get()
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'Skipping redirect %s' % refpl.linkname())
            pass
        except wikipedia.LockedPage:
            wikipedia.output(u'Skipping locked page %s' % refpl.linkname())
            pass
        except wikipedia.NoPage:
            wikipedia.output('Page %s not found' % refpl.linkname())
            pass
        else:
            # Check if template is really used in this article
            if not self.templateR.search(reftxt):
                wikipeida.output("Not found in %s" % refpl.linkname())
                return
            
            # Replace all occurences of the template in this article
            if self.remove:
                reftxt = re.sub(self.templateR, '', reftxt)
            elif self.resolve:
                reftxt = re.sub(self.templateR, '{{subst:' + self.old + '}}', reftxt)
            elif self.oldFormat:
                reftxt = re.sub(self.templateR, '{{msg:' + self.new + '}}', reftxt)
            else:
                reftxt = re.sub(self.templateR, '{{' + self.new + '}}', reftxt)
    
            refpl.put(reftxt)
        
def main():
    oldFormat = False
    template_names = []
    resolve = False
    remove = False
    # If sqlfilename is None, references will be loaded from the live wiki.
    sqlfilename = None
    new = None
    # read command line parameters
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg == '-remove':
                remove = True
            elif arg == '-oldformat':
                oldFormat = True
            elif arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
                else:
                    sqlfilename = arg[5:]
            else:
                template_names.append(arg)

    if len(template_names) == 0 or len(template_names) > 2:
        wikipedia.output(__doc__, 'utf-8')
        wikipedia.stopme()
        sys.exit()
    old = template_names[0]
    if len(template_names) == 2:
        new = template_names[1]

    gen = TemplatePageGenerator(old, sqlfilename)
    bot = TemplateRobot(gen, old, new, remove, oldFormat)
    bot.run()

try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()
