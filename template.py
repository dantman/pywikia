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

class XmlDumpTemplatePageGenerator:
    """
    Generator which will yield Pages to pages that might contain the chosen
    template. These pages will be retrieved from a local XML dump file
    (cur table).
    """
    def __init__(self, template, xmlfilename):
        """
        Arguments:
            * template    - A Page object representing the searched template
            * xmlfilename - The dump's path, either absolute or relative
        """
        self.template = template
        self.xmlfilename = xmlfilename

    def __iter__(self):
        """
        Yield page objects until the entire XML dump has been read.
        """
        import xmlreader
        mysite = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlfilename)
        # regular expression to find the original template.
        # {{vfd}} does the same thing as {{Vfd}}, so both will be found.
        # The old syntax, {{msg:vfd}}, will also be found.
        # TODO: check site.nocapitalize()
        templateName = self.template.titleWithoutNamespace()
        if wikipedia.getSite().nocapitalize:
            old = self.old
        else:
            templateName = '[' + templateName[0].upper() + templateName[0].lower() + ']' + templateName[1:]
        templateName = re.sub(' ', '[_ ]', templateName)
        templateRegex = re.compile(r'\{\{([mM][sS][gG]:)?' + templateName + '(?P<parameters>\|[^}]+|)}}')
        for entry in dump.parse():
            if templateRegex.search(entry.text):
                page = wikipedia.Page(mysite, entry.title)
                yield page

class TemplateRobot:
    """
    This robot will load all pages yielded by a page generator and replace or
    remove all occurences of the old template, or substitute them with the
    template's text.
    """
    # Summary messages
    msg_change={
        'en':u'Robot: Changing template: %s',
        'de':u'Bot: Ändere Vorlage: %s',
		'fr':u'Robot: Changement de modèle: %s',
		'ia':u'Robot: Modification del template: %s',
        'hu':u'Robot: Sablon csere: %s',
        'pt':u'Bot: Alterando predefinição: %s',
        }
    
    msg_remove={
        'en':u'Robot: Removing template: %s',
        'de':u'Bot: Entferne Vorlage: %s',
		'fr':u'Robot: Enlève le modèle: %s',
		'ia':u'Robot: Elimination del template: %s',
        'hu':u'Robot: Sablon eltávolítása: %s',
        'pt':u'Bot: Removendo predefinição: %s',
        }

    def __init__(self, generator, old, new = None, remove = False):
        """
        Arguments:
            * generator - A page generator.
            * old       - The title of the old template (without namespace)
            * new       - The title of the new template (without namespace), or
                          None if you want to substitute the template with its
                          text.
            * remove    - True if the template should be removed.
        """
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
        """
        Starts the robot's action.
        """
        # regular expression to find the original template.
        # {{vfd}} does the same thing as {{Vfd}}, so both will be found.
        # The old syntax, {{msg:vfd}}, will also be found.
        # The group 'parameters' will either match the parameters, or an
        # empty string if there are none.
        if wikipedia.getSite().nocapitalize:
            old = self.old
        else:
            old = '[' + self.old[0].upper() + self.old[0].lower() + ']' + self.old[1:]
        old = re.sub('[_ ]', '[_ ]', old)
        templateRegex = re.compile(r'\{\{([mM][sS][gG]:)?' + old + '(?P<parameters>\|[^}]+|)}}')
        replacements = []
        if self.remove:
            replacements.append((templateRegex, ''))
        elif self.resolve:
            replacements.append((templateRegex, '{{subst:' + self.old + '\g<parameters>}}'))
        else:
            replacements.append((templateRegex, '{{' + self.new + '\g<parameters>}}'))
        replaceBot = replace.ReplaceRobot(self.generator, replacements)
        replaceBot.run()
    
def main():
    template_names = []
    resolve = False
    remove = False
    # If xmlfilename is None, references will be loaded from the live wiki.
    xmlfilename = None
    new = None
    # read command line parameters
    for arg in wikipedia.handleArgs():
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
        wikipedia.showHelp()
        sys.exit()
    old = template_names[0]
    if len(template_names) == 2:
        new = template_names[1]

    mysite = wikipedia.getSite()
    ns = mysite.template_namespace()
    oldTemplate = wikipedia.Page(mysite, ns + ':' + old)

    if xmlfilename:
        gen = XmlDumpTemplatePageGenerator(oldTemplate, xmlfilename)
    else:
        gen = pagegenerators.ReferringPageGenerator(oldTemplate, onlyTemplateInclusion = True)
    preloadingGen = pagegenerators.PreloadingGenerator(gen)
    bot = TemplateRobot(preloadingGen, old, new, remove)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
