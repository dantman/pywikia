#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This script goes over multiple pages, searches for pages where <references/>
is missing although a <ref> tag is present, and in that case adds a new
references section.

These command line parameters can be used to specify which pages to work on:

&params;

    -xml           Retrieve information from a local XML dump (pages-articles
                   or pages-meta-current, see http://download.wikimedia.org).
                   Argument can also be given as "-xml:filename".

    -namespace:n   Number of namespace to process. The parameter can be used
                   multiple times. It works in combination with all other
                   parameters, except for the -start parameter. If you e.g.
                   want to iterate over all categories starting at M, use
                   -start:Category:M.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.

It is strongly recommended not to run this script over the entire article
namespace (using the -start) parameter, as that would consume too much
bandwidth. Instead, use the -xml parameter, or use another way to generate
a list of affected articles
"""

__version__='$Id: selflink.py 4187 2007-09-03 11:37:19Z wikipedian $'

import wikipedia, pagegenerators, catlib
import editarticle
import re, sys

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}

# Summary messages in different languages
msg = {
    'de':u'Bot: Trage fehlendes <references /> nach',
    'en':u'Robot: Adding missing <references /> tag',
}

# References sections are usually placed before further reading / external
# link sections. This dictionary defines these sections, sorted by priority.
# For example, on an English wiki, the script would place the "References"
# section in front of the "Further reading" section, if that existed.
# Otherwise, it would try to do it 
placeBeforeSection = {
    'de': [              # no explicit policy on where to put the references
        u'Literatur',
        u'Weblinks',
        u'Siehe auch'
    ],
    'en': [              # no explicit policy on where to put the references
        u'Further reading',
        u'External links',
        u'See also',
        u'Notes'
    ],
}

# How the references section should look like.
referencesSection = {
    'de': u'\n== Einzelnachweise ==\n\n<references/>\n', # The "Einzelnachweise" title is disputed, some people prefer "Quellen", "Quellenangaben", "Fußnoten", etc.
    'en': u'\n== References ==\n\n<references/>\n',
}

# Templates which include a <references/> tag. If there is no such template
# on your wiki, you don't have to enter anything here.
referencesTemplates = {
    'wikipedia': {
        'en': [u'Reflist'],
    },
}

class XmlDumpNoReferencesPageGenerator:
    """
    Generator which will yield Pages that might lack a references tag.
    These pages will be retrieved from a local XML dump file
    (pages-articles or pages-meta-current).
    """
    def __init__(self, xmlFilename):
        """
        Arguments:
            * xmlFilename  - The dump's path, either absolute or relative
        """
        self.xmlFilename = xmlFilename
        self.refR = re.compile('</ref>')
        self.referencesR = re.compile('<references */>')

    def __iter__(self):
        import xmlreader
        mysite = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlFilename)
        for entry in dump.parse():
            if self.refR.search(entry.text) and not self.referencesR.search(entry.text):
                yield wikipedia.Page(mysite, entry.title)

class NoReferencesBot:

    def __init__(self, generator, always = False):
        self.generator = generator
        self.always = always

        self.refR = re.compile('</ref>')
        self.referencesR = re.compile('<references */>')
        try:
            self.referencesTemplates = referencesTemplates[wikipedia.getSite().family.name][wikipedia.getSite().lang]
        except KeyError:
            self.referencesTemplates = []

    def needsTreatment(self, page):
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
        try:
            oldText = page.get()
            oldTextCleaned = wikipedia.removeDisabledParts(oldText)
            if not self.refR.search(oldTextCleaned):
                wikipedia.output(u'No changes necessary: no ref tags found.')
                return False
            elif self.referencesR.search(oldTextCleaned):
                wikipedia.output(u'No changes necessary: references tags found.')
                return False
            else:
                for template in page.templates():
                    if template in self.referencesTemplates:
                        wikipedia.output(u'No changes necessary: references template found.')
                        return False
                wikipedia.output(u'Found ref without references.')
                return True
        except wikipedia.NoPage:
            wikipedia.output(u"Page %s does not exist?!" % page.aslink())
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"Page %s is a redirect; skipping." % page.aslink())
        except wikipedia.LockedPage:
            wikipedia.output(u"Page %s is locked?!" % page.aslink())
        return False

    def treat(self, page):
        oldText = page.get()
        for section in wikipedia.translate(wikipedia.getSite(), placeBeforeSection):
            sectionR = re.compile(r'\r\n=+ +%s +=+' % section)
            match = sectionR.search(oldText)
            if match:
                wikipedia.output(u'Adding references section...\n')
                pos = match.start()
                newSection = wikipedia.translate(wikipedia.getSite(), referencesSection)
                newText = oldText[:match.start()] + newSection + oldText[match.start():]
                wikipedia.showDiff(oldText, newText)
                if not self.always:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'Always yes'], ['y', 'N', 'a'], 'N')
                    if choice == 'n':
                        return
                    elif choice == 'a':
                        self.always = True

                if self.always:
                    try:
                        page.put(newText)
                    except wikipedia.EditConflict:
                        wikipedia.output(u'Skipping %s because of edit conflict' % (page.title(),))
                    except wikipedia.SpamfilterError, e:
                        wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
                    except wikipedia.LockedPage:
                        wikipedia.output(u'Skipping %s (locked page)' % (page.title(),))
                else:
                    # Save the page in the background. No need to catch exceptions.
                    page.put_async(newText)
                return
        # TODO: Think of a more clever way of doing this.
        wikipedia.output(u'Found no section that can be preceeded by a new references section. Please fix it manually.')
        

    def run(self):
        comment = wikipedia.translate(wikipedia.getSite(), msg)
        wikipedia.setAction(comment)

        for page in self.generator:
            if self.needsTreatment(page):
                self.treat(page)

def main():
    #page generator
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitle = []
    # Which namespaces should be processed?
    # default to [] which means all namespaces will be processed
    namespaces = []
    # Never ask before changing a page
    always = False
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
            gen = XmlDumpNoReferencesPageGenerator(xmlFilename)
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))
        elif arg == '-always':
            always = True
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
            else:
                pageTitle.append(arg)

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('noreferences')
    else:
        if namespaces != []:
            gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = NoReferencesBot(preloadingGen, always = always)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
 
