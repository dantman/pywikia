#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This script can move pages.

These command line parameters can be used to specify which pages to work on:

&params;

Furthermore, the following command line parameters are supported:

-from and -to     The page to move from and the page to move to.

-del              After moving the page, delete the redirect.

-prefix           Move pages by adding a namespace prefix to the names of the pages.
                  (Will remove the old namespace prefix if any)
                  Argument can also be given as "-prefix:namespace:".

-always           Don't prompt to make changes, just do them.

"""
#
# (C) Leonardo Gregianin, 2006
# (C) Andreas J. Schwab, 2007
#
# Distributed under the terms of the MIT license.
#

__version__='$Id$'

import wikipedia, pagegenerators, catlib, config
import sys
import re

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}

summary={
    'ar': u'نقل الصفحة بواسطة البوت',
    'en': u'Robot: moved page',
    'de': u'Bot: Seite verschoben',
    'el': u'Μετακίνηση σελίδων με bot',
    'fr': u'Bot: Page renommée',
    'he': u'העברת דף באמצעות בוט',
    'nl': u'Bot: paginatitel gewijzigd',
    'pl': u'Przeniesienie artykułu przez robota',
    'pt': u'Bot: Página movida',
}

deletesummary={
    'de': u'Bot: Lösche nach Seitenverschiebung nicht benötigte Umleitung',
    'en': u'Robot: Deleting redirect after page has been moved'
    # These are too unspecific:
    #'ar': u'حذف الصفحة بواسطة البوت',
    #'en': u'Robot: deleted page',
    #'de': u'Bot: Seite gelöscht',
    #'el': u'Διαγραφή σελίδων με bot',
    #'fr': u'Page supprimée par bot',
    #'nl': u'Pagina verwijderd door robot',
    #'pl': u'Usunięcie artykułu przez robota',
    #'pt': u'Página apagada por bot',
}

class MovePagesBot:
    def __init__(self, generator, addprefix, delete, always):
        self.generator = generator
        self.addprefix = addprefix
        self.delete = delete
        self.always = always

    def moveOne(self, page, newPageTitle,delete):
        try:
            msg = wikipedia.translate(wikipedia.getSite(), summary)
            wikipedia.output(u'Moving page %s to [[%s]]' % (page.aslink(), newPageTitle))
            page.move(newPageTitle, msg, throttle=True)
            if delete:
                deletemsg = wikipedia.translate(wikipedia.getSite(), deletesummary)
                page.delete(deletemsg)
        except wikipedia.NoPage:
            wikipedia.output(u'Page %s does not exist!' % page.title())
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
        except wikipedia.LockedPage:
            wikipedia.output(u'Page %s is locked!' % page.title())

    def treat(self, page):
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"% page.title())
        pagetitle = page.titleWithoutNamespace()
        namesp = page.site().namespace(page.namespace())
        if self.appendAll:
            newPageTitle = (u'%s%s%s' % (self.pagestart, pagetitle, self.pageend))
            if not self.noNamespace and namesp:
                newPageTitle = (u'%s:%s' % (namesp, newPageTitle))
        elif self.regexAll:
            newPageTitle = self.regex.sub(self.replacePattern, pagetitle)
            if not self.noNamespace and namesp:
                newPageTitle = (u'%s:%s' % (namesp, newPageTitle))
        if self.addprefix:
            newPageTitle = (u'%s%s' % (self.addprefix, pagetitle))
        if self.addprefix or self.appendAll or self.regexAll:
            if not self.always:
                choice2 = wikipedia.inputChoice(u'Change the page title to "%s"?' % newPageTitle, ['yes', 'no', 'quit'], ['y', 'n', 'q'])
                if choice2 == 'y':
                    self.moveOne(page,newPageTitle,self.delete)
                elif choice2 == 'q':
                    sys.exit()
                elif choice2 == 'n':
                    pass
                else:
                    self.treat(page)
            else:
                self.moveOne(page,newPageTitle,self.delete)
        else:
            choice = wikipedia.inputChoice(u'What do you want to do?', ['change page name', 'append to page name', 'use a regular expression', 'next page', 'quit'], ['c', 'a', 'r', 'n', 'q'])
            if choice == 'c':
                newPageTitle = wikipedia.input(u'New page name:')
                self.moveOne(page,newPageTitle,self.delete)
            elif choice == 'a':
                self.pagestart = wikipedia.input(u'Append this to the start:')
                self.pageend = wikipedia.input(u'Append this to the end:')
                newPageTitle = (u'%s%s%s' % (self.pagestart, pagetitle, self.pageend))
                if namesp:
                    choice2 = wikipedia.inputChoice(u'Do you want to remove the namespace prefix "%s:"?' % namesp, ['yes', 'no'], ['y', 'n'])
                    if choice2 == 'y':
                        noNamespace = True
                    else:
                        newPageTitle = (u'%s:%s' % (namesp, newPageTitle))
                choice2 = wikipedia.inputChoice(u'Change the page title to "%s"?' % newPageTitle, ['yes', 'no', 'all', 'quit'], ['y', 'n', 'a', 'q'])
                if choice2 == 'y':
                    self.moveOne(page,newPageTitle,self.delete)
                elif choice2 == 'a':
                    self.appendAll = True
                    self.moveOne(page,newPageTitle,self.delete)
                elif choice2 == 'q':
                    sys.exit()
                elif choice2 == 'n':
                    pass
                else:
                    self.treat(page)
            elif choice == 'r':
                searchPattern = wikipedia.input(u'Enter the search pattern:')
                self.replacePattern = wikipedia.input(u'Enter the replace pattern:')
                self.regex=re.compile(searchPattern)
                if page.title() == page.titleWithoutNamespace():
                    newPageTitle = self.regex.sub(self.replacePattern, page.title())
                else:
                    choice2 = wikipedia.inputChoice(u'Do you want to remove the namespace prefix "%s:"?' % namesp, ['yes', 'no'], ['y', 'n'])
                    if choice2 == 'y':
                        newPageTitle = self.regex.sub(self.replacePattern, page.titleWithoutNamespace())
                        noNamespace = True
                    else:
                        newPageTitle = self.regex.sub(self.replacePattern, page.title())
                choice2 = wikipedia.inputChoice(u'Change the page title to "%s"?' % newPageTitle, ['yes', 'no', 'all', 'quit'], ['y', 'n', 'a', 'q'])
                if choice2 == 'y':
                    self.moveOne(page,newPageTitle,self.delete)
                elif choice2 == 'a':
                    self.regexAll = True
                    self.moveOne(page,newPageTitle,self.delete)
                elif choice2 == 'q':
                    sys.exit()
                elif choice2 == 'n':
                    pass
                else:
                    self.treat(page)
            elif choice == 'n':
                pass
            elif choice == 'q':
                sys.exit()
            else:
                self.treat(page)

    def run(self):
        self.appendAll = False
        self.regexAll = False
        self.noNamespace = False
        for page in self.generator:
            self.treat(page)

def main():
    gen = None
    prefix = None
    oldName = None
    newName = None
    delete = False
    always = False

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg == '-del':
            delete = True
        elif arg == '-always':
            always = True
        elif arg.startswith('-from:'):
            oldName = arg[len('-from:'):]
        elif arg.startswith('-to:'):
            newName = arg[len('-to:'):]
        elif arg.startswith('-prefix'):
            if len(arg) == len('-prefix'):
                prefix = wikipedia.input(u'Enter the prefix:')
            else:
                prefix = arg[8:]
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator

    if oldName and newName:
        page = wikipedia.Page(wikipedia.getSite(), oldName)
        bot = MovePagesBot(None, prefix, delete, always)
        bot.moveOne(page, newName, delete)
    elif gen:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = MovePagesBot(preloadingGen, prefix, delete, always)
        bot.run()
    else:
        wikipedia.showHelp('movepages')

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()