# -*- coding: utf-8 -*-
"""
Very simple script to replace a template with another one,
and to convert the old MediaWiki boilerplate format to the new template format.

Syntax: python template.py [-remove] [xml[:filename]] oldTemplate [newTemplate]

Specify the template on the command line. The program will
pick up the template page, and look for all pages using it. It will
then automatically loop over them, and replace the template.

Command line options:

-remove    - Remove every occurence of the template from every article

-xml       - retrieve information from a local dump (http://download.wikimedia.org).
             if this argument isn\'t given, info will be loaded from the maintenance
             page of the live wiki.
             argument can also be given as "-xml:filename.xml".

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
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#
import wikipedia, config
import replace, pagegenerators
import re, sys, string

class XmlTemplatePageGenerator:
    def __init__(self, template, xmlfilename):
        self.template = template
        self.xmlfilename = xmlfilename

    def __iter__(self):
        import xmlreader
        mysite = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlfilename)
        # regular expression to find the original template.
        # {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
        # The new syntax, {{vfd}}, will also be found.
        templateName = self.template.title().split(':', 1)[1]
        templateRegex = re.compile('\{\{([mM][sS][gG]:)?[' + templateName[0].upper() + templateName[0].lower() + ']' + templateName[1:] + '}}')
        for entry in dump.parse():
            if templateRegex.search(entry.text):
                page = wikipedia.Page(mysite, entry.title)
                yield page

class TemplateRobot:
    # Summary messages
    msg_change={
        'en':u'Robot: Changing template: %s',
        'de':u'Bot: Ändere Vorlage: %s',
		'fr':u'Robot: Changement de modèle: %s',
        'pt':u'Bot: Alterando predefinição: %s',
        }
    
    msg_remove={
        'en':u'Robot: Removing template: %s',
        'de':u'Bot: Entferne Vorlage: %s',
		'fr':u'Robot: Enlève le modèle: %s',
        'pt':u'Bot: Removendo predefinição: %s',
        }

    def __init__(self, generator, old, new = None, remove = False):
        self.generator = generator
        self.old = old
        self.new = new
        self.remove = remove
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
        # regular expression to find the original template.
        # {{msg:vfd}} does the same thing as {{msg:Vfd}}, so both will be found.
        # The new syntax, {{vfd}}, will also be found.
        # The group 'parameters' will either match the parameters, or an
        # empty string if there are none.
        if not wikipedia.getSite().nocapitalize:
            old = '[' + self.old[0].upper() + self.old[0].lower() + ']' + self.old[1:]
        else:
            old = self.old
        old = re.sub('[_ ]', '[_ ]', old)
        templateR=re.compile(r'\{\{([mM][sS][gG]:)?' + old + '(?P<parameters>\|[^}]+|)}}')
        replacements = []
        if self.remove:
            replacements.append((templateR, ''))
        elif self.resolve:
            replacements.append((templateR, '{{subst:' + self.old + '}}'))
        else:
            replacements.append((templateR, '{{' + self.new + '\g<parameters>}}'))
        replaceBot = replace.ReplaceRobot(self.generator, replacements, regex = True)
        replaceBot.run()
    
def main():
    template_names = []
    resolve = False
    remove = False
    # If xmlfilename is None, references will be loaded from the live wiki.
    xmlfilename = None
    new = None
    # read command line parameters
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'template')
        if arg:
            if arg == '-remove':
                remove = True
            elif arg.startswith('-xml'):
                if len(arg) == 4:
                    xmlfilename = wikipedia.input(u'Please enter the XML dump\'s filename: ')
                else:
                    xmlfilename = arg[5:]
            else:
                template_names.append(arg)

    if len(template_names) == 0 or len(template_names) > 2:
        wikipedia.showHelp('template')
        sys.exit()
    old = template_names[0]
    if len(template_names) == 2:
        new = template_names[1]

    mysite = wikipedia.getSite()
    ns = mysite.template_namespace(fallback = None)
    oldTemplate = wikipedia.Page(mysite, ns + ':' + old)

    if xmlfilename:
        gen = XmlTemplatePageGenerator(oldTemplate, xmlfilename)
    else:
        gen = pagegenerators.ReferringPageGenerator(oldTemplate)
    preloadingGen = pagegenerators.PreloadingGenerator(gen)
    bot = TemplateRobot(preloadingGen, old, new, remove)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
