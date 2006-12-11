# -*- coding: utf-8 -*-
"""
Very simple script to replace a template with another one,
and to convert the old MediaWiki boilerplate format to the new template format.

Syntax: python template.py [-remove] [xml[:filename]] oldTemplate [newTemplate]

Specify the template on the command line. The program will
pick up the template page, and look for all pages using it. It will
then automatically loop over them, and replace the template.

Command line options:

-remove      Remove every occurence of the template from every article

-xml         retrieve information from a local dump (http://download.wikimedia.org).
             if this argument isn\'t given, info will be loaded from the maintenance
             page of the live wiki.
             argument can also be given as "-xml:filename.xml".

-namespace:  Only process templates in the given namespace number (may be used
             multiple times).

-summary:    Lets you pick a custom edit summary.  Use quotes if edit summary contains
             spaces.

-always      Don't bother asking to confirm any of the changes, Just Do It.

-page:       Only edit a specific page.  You can use this argument multiple times to work
             on multiple pages.  If the page title has spaces in it, enclose the entire
             page name in quotes.

-extras      Specify this to signal that all parameters are templates that should either be
             substituted or removed.  Allows you to input way more than just two.  Not
             compatible with -xml (yet)  Disables template replacement.

other:       First argument is the old template name, second one is the new
             name. If only one argument is given, the bot resolves the
             template by putting its text directly into the article.
             This is done by changing {{...}} or {{msg:...}} into {{subst:...}}
             
             If you want to address a template which has spaces, put quotation
             marks around it.
             
Examples:

If you have a template called [[Template:Cities in Washington]] and want to
change it to [[Template:Cities in Washington state]], start

    python template.py "Cities in Washington" "Cities in Washington state"

Move the page [[Template:Cities in Washington]] manually afterwards.


If you have a template called [[Template:test]] and want to substitute it only on pages
in the User: and User talk: namespaces, do:

    python template.py test -namespace:2 -namespace:3

Note that, on the English Wikipedia, User: is namespace 2 and User talk: is namespace 3.
This may differ on other projects so make sure to find out the appropriate namespace numbers.


This next example substitutes the template lived with a supplied edit summary.  It only
performs substitutions in main article namespace and doesn't prompt to start replacing.
Note that -putthrottle: is a global pywikipedia parameter.

    python template.py -putthrottle:30 -namespace:0 lived -always
        -summary:"ROBOT: Substituting {{lived}}, see [[WP:SUBST]]."


This next example removes the templates {{cfr}}, {{cfru}}, and {{cfr-speedy}} from five
category pages as given:

    python template.py cfr cfru cfr-speedy -remove -always -extras
        -page:"Category:Mountain monuments and memorials" -page:"Category:Indian family names"
        -page:"Category:Tennis tournaments in Belgium" -page:"Category:Tennis tournaments in Germany"
        -page:"Category:Episcopal cathedrals in the United States"
        -summary:"Removing Cfd templates from category pages that survived."


This next example substitutes templates test1, test2, and space test on all pages:

    python template.py test1 test2 "space test" -always -extras

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
        templateRegex = re.compile(r'\{\{ *([mM][sS][gG]:)?' + templateName + ' *(?P<parameters>\|[^}]+|) *}}')
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
    # Summary messages for replacing templates
    msg_change={
        'en':u'Robot: Changing template: %s',
        'de':u'Bot: Ändere Vorlage: %s',
	'fr':u'Robot: Changement de modèle: %s',
        'he':u'רובוט: משנה תבנית: %s',
	'ia':u'Robot: Modification del template: %s',
        'hu':u'Robot: Sablon csere: %s',
        'lt':u'robotas: Keičiamas šablonas: %s',
        'pt':u'Bot: Alterando predefinição: %s',
        'sr':u'Бот: Измена шаблона: %s',
    }

    #Needs more translations!
    msgs_change={
	'en':u'Robot: Changing templates: %s',
        'he':u'רובוט: משנה תבניות: %s',
        'lt':u'robotas: Keičiami šablonai: %s',
        'pt':u'Bot: Alterando predefinição: %s',
    }
    
    # Summary messages for removing templates
    msg_remove={
        'en':u'Robot: Removing template: %s',
        'de':u'Bot: Entferne Vorlage: %s',
        'fr':u'Robot: Enlève le modèle: %s',
        'he':u'רובוט: מסיר תבנית: %s', 
        'ia':u'Robot: Elimination del template: %s',
        'hu':u'Robot: Sablon eltávolítása: %s',
        'lt':u'robotas: Šalinamas šablonas: %s',
        'pt':u'Bot: Removendo predefinição: %s',
        'sr':u'Бот: Уклањање шаблона: %s',
    }

    #Needs more translations!
    msgs_remove={
        'en':u'Robot: Removing templates: %s',
        'he':u'רובוט: מסיר תבניות: %s',
        'lt':u'robotas: Šalinami šablonai: %s',
        'pt':u'Bot: Removendo predefinição: %s',
    }

    # Summary messages for substituting templates
    #Needs more translations!
    msg_subst={
        'en':u'Robot: Substituting template: %s',
        'he':u'רובוט: מכליל תבנית בקוד הדף: %s',
        'pt':u'Bot: Substituindo predefinição: %s',
    }

    #Needs more translations!
    msgs_subst={
        'en':u'Robot: Substituting templates: %s',
        'he':u'רובוט: מכליל תבניות בקוד הדף: %s',
        'pt':u'Bot: Substituindo predefinição: %s',
    }

    def __init__(self, generator, old, new = None, remove = False, editSummary = '', acceptAll = False, extras = False):
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
        self.editSummary = editSummary
        self.acceptAll = acceptAll
        self.extras = extras
        # if only one argument is given, don't replace the template with another
        # one, but resolve the template by putting its text directly into the
        # article.
        self.resolve = (new == None)

        # get edit summary message
	if isinstance(self.old, list):
	    allTemplates = (', ').join(old)
	else:
	    allTemplates = old
	if self.editSummary:
	    wikipedia.setAction(self.editSummary)
	else:
	    mysite = wikipedia.getSite()
            if self.remove:
		if self.extras:
		    wikipedia.setAction(wikipedia.translate(mysite, self.msgs_remove) % allTemplates)
		else:
               	    wikipedia.setAction(wikipedia.translate(mysite, self.msg_remove) % allTemplates)
	    elif self.resolve:
		if self.extras:
		    wikipedia.setAction(wikipedia.translate(mysite, self.msgs_subst) % allTemplates)
		else:
               	    wikipedia.setAction(wikipedia.translate(mysite, self.msg_subst) % allTemplates)
            else:
		if self.extras:
		    wikipedia.setAction(wikipedia.translate(mysite, self.msgs_change) % allTemplates)
		else:
                    wikipedia.setAction(wikipedia.translate(mysite, self.msg_change) % allTemplates)

    def run(self):
        """
        Starts the robot's action.
        """
        # regular expression to find the original template.
        # {{vfd}} does the same thing as {{Vfd}}, so both will be found.
        # The old syntax, {{msg:vfd}}, will also be found.
        # The group 'parameters' will either match the parameters, or an
        # empty string if there are none.

        replacements = []
	if not isinstance(self.old, list):
	    self.old = [self.old]

	for old in self.old:
	    oldOld = old
            if not wikipedia.getSite().nocapitalize:
                old = '[' + old[0].upper() + old[0].lower() + ']' + old[1:]
            old = re.sub('[_ ]', '[_ ]', old)
            templateRegex = re.compile(r'\{\{ *(?:[Tt]emplate:|[mM][sS][gG]:)?' + old + ' *(?P<parameters>\|[^}]+|) *}}')

            if self.remove:
                replacements.append((templateRegex, ''))
            elif self.resolve:
                replacements.append((templateRegex, '{{subst:' + oldOld + '\g<parameters>}}'))
            else:
                replacements.append((templateRegex, '{{' + self.new + '\g<parameters>}}'))

        #Note that the [] parameter here is for exceptions (see replace.py).  For now we don't use it.
        replaceBot = replace.ReplaceRobot(self.generator, replacements, [], self.acceptAll)
        replaceBot.run()

def main():
    template_names = []
    resolve = False
    remove = False
    namespaces = []
    editSummary = ''
    acceptAll = False
    pageTitles = []
    extras = False
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
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[len('-namespace:'):]))
        elif arg.startswith('-summary:'):
            editSummary = arg[len('-summary:'):]
        elif arg.startswith('-always'):
            acceptAll = True
        elif arg.startswith('-page'):
            if len(arg) == len('-page'):
                pageTitles.append(wikipedia.input(u'Which page do you want to chage?'))
            else:
                pageTitles.append(arg[len('-page:'):])
        elif arg.startswith('-extras'):
            extras = True
        else:
            template_names.append(arg)

    if extras:
        old = template_names
    elif len(template_names) == 0 or len(template_names) > 2:
        wikipedia.showHelp()
        sys.exit()
    else:
        old = template_names[0]
        if len(template_names) == 2:
            new = template_names[1]

    mysite = wikipedia.getSite()
    ns = mysite.template_namespace()

    if extras:
        oldTemplate = []
            for thisPage in old:
                oldTemplate.append(wikipedia.Page(mysite, ns + ':' + thisPage))
    else:
        oldTemplate = wikipedia.Page(mysite, ns + ':' + old)

    if xmlfilename:
        gen = XmlDumpTemplatePageGenerator(oldTemplate, xmlfilename)
    elif pageTitles:
        pages = [wikipedia.Page(wikipedia.getSite(), pageTitle) for pageTitle in pageTitles]
        gen = iter(pages)
    elif extras:
        gen = pagegenerators.ReferringPagesGenerator(oldTemplate, onlyTemplateInclusion = True)
    else:
        gen = pagegenerators.ReferringPageGenerator(oldTemplate, onlyTemplateInclusion = True)

    if namespaces:
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)

    preloadingGen = pagegenerators.PreloadingGenerator(gen)

    #At this point, if extras is set to False, old is the name of a single template.
    #But if extras is set to True, old is a whole list of templates to be replaced.
    bot = TemplateRobot(preloadingGen, old, new, remove, editSummary, acceptAll, extras)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
