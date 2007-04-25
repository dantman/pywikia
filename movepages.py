#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot page moves to another title.

Command-line arguments:

    -file          Work on all pages listed in a text file.
                   Argument can also be given as "-file:filename".

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

    -links         Work on all pages that are linked from a certain page.
                   Argument can also be given as "-link:linkingpagetitle".

    -link          same as -links (deprecated)

    -start         Work on all pages on the home wiki, starting at the named page.

    -from -to      The page to move from and the page to move to.

    -new           Work on the most recent new pages on the wiki.

    -del           Argument can be given also together with other arguments,
                   its functionality is delete old page that was moved.
                   For example: "movepages.py pagetitle -del".

    -prefix        Move pages by adding a namespace prefix to the names of the pages.
                   (Will remove the old namespace prefix if any)
                   Argument can also be given as "-prefix:namespace:".

    -always        Don't prompt to make changes, just do them.

Single page use:   movepages.py pagetitle1 pagetitle2 ...

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

summary={
    'en': u'Pagemove by bot',
    'de': u'Seite durch Bot verschoben',
    'el': u'Μετακίνηση σελίδων με bot',
    'fr': u'Page renommée par bot',
    'he': u'העברת דף באמצעות בוט',
    'nl': u'Pagina hernoemd door robot',
    'pl': u'Przeniesienie artykułu przez robota',
    'pt': u'Página movida por bot',
}

deletesummary={
    'en': u'Delete page by bot',
    'de': u'Seite durch Bot gelöscht',
    'el': u'Διαγραφή σελίδων με bot',
    'fr': u'Page supprimée par bot',
    'nl': u'Pagina verwijderd door robot',
    'pl': u'Usunięcie artykułu przez robota',
    'pt': u'Página apagada por bot',
}

class MovePagesBot:
    def __init__(self, generator, prefix, delete, always):
        self.generator = generator
        self.prefix = prefix
        self.delete = delete
        self.always = always


    def moveOne(self,page,pagemove,delete):
        try:
            msg = wikipedia.translate(wikipedia.getSite(), summary)
            wikipedia.output(u'Moving page %s' % page.title())
            wikipedia.output(u'to page %s' % pagemove)
            page.move(pagemove, msg, throttle=True)
            if delete == True:
                deletemsg = wikipedia.translate(wikipedia.getSite(), deletesummary)
                page.delete(deletemsg)
        except wikipedia.NoPage:
            wikipedia.output('Page %s does not exist!' % page.title())
        except wikipedia.IsRedirectPage:
            wikipedia.output('Page %s is a redirect; skipping.' % page.title())
        except wikipedia.LockedPage:
            wikipedia.output('Page %s is locked!' % page.title())

    def treat(self,page):
        pagetitle = page.title()
        wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
        if self.prefix:
            pagetitle = page.titleWithoutNamespace()
            pagemove = (u'%s%s' % (self.prefix, pagetitle))
            if self.always == False:
                ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o, (Q)uit]' % pagemove)
                if ask2 in ['y', 'Y']:
                    self.moveOne(page,pagemove,self.delete)
                elif ask2 in ['q', 'Q']:
                    sys.exit()
                elif ask2 in ['n', 'N']:
                    pass
                else:
                    self.treat(page)
            else:
                self.moveOne(page,pagemove,self.delete)
        elif self.appendAll == False:
            ask = wikipedia.input('What do you want to do: (c)hange page name, (a)ppend to page name, (n)ext page or (q)uit?')
            if ask in ['c', 'C']:
                pagemove = wikipedia.input(u'New page name:')
                self.moveOne(page,pagemove,self.delete)
            elif ask in ['a', 'A']:
                self.pagestart = wikipedia.input(u'Append This to the start:')
                self.pageend = wikipedia.input(u'Append This to the end:')
                if page.title() == page.titleWithoutNamespace():
                    pagemove = (u'%s%s%s' % (self.pagestart, page.title(), self.pageend))
                else:
                    ask2 = wikipedia.input(u'Do you want to remove the namespace prefix "%s:"? [(Y)es, (N)o]'% page.site().namespace(page.namespace()))
                    if ask2 in ['y', 'Y']:
                        pagemove = (u'%s%s%s' % (self.pagestart, page. titleWithoutNamespace(), self.pageend))
                    else:
                        pagemove = (u'%s%s%s' % (self.pagestart, page.title(), self.pageend))
                ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o, (A)ll, (Q)uit]' % pagemove)
                if ask2 in ['y', 'Y']:
                    self.moveOne(page,pagemove,self.delete)
                elif ask2 in ['a', 'A']:
                    self.appendAll = True
                    self.moveOne(page,pagemove,self.delete)
                elif ask2 in ['q', 'Q']:
                    sys.exit()
                elif ask2 in ['n', 'N']:
                    pass
                else:
                    self.treat(page)
            elif ask in ['n', 'N']:
                pass
            elif ask in ['q', 'Q']:
                sys.exit()
            else:
                self.treat(page)
        else:
            pagemove = (u'%s%s%s' % (self.pagestart, page.title(), self.pageend))
            if self.always == False:
                ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o, (Q)uit]' % pagemove)
                if ask2 in ['y', 'Y']:
                    self.moveOne(page,pagemove,self.delete)
                elif ask2 in ['q', 'Q']:
                    sys.exit()
                elif ask2 in ['n', 'N']:
                    pass
                else:
                    self.treat(page)
            else:
                self.moveOne(page,pagemove,self.delete)

    def run(self):
        self.appendAll = False
        for page in self.generator:
            self.treat(page)

def main():
    singlepage = []
    gen = None
    prefix = None
    FromName = ToName = None
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
            FromName = True
        elif arg.startswith('-to:'):
            newName = arg[len('-to:'):]
            ToName = True
        elif arg.startswith('-prefix'):
            if len(arg) == len('-prefix'):
                prefix = wikipedia.input(u'Input the prefix:')
            else:
                prefix = arg[8:]
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
            else:
                singlepage.append(wikipedia.Page(wikipedia.getSite(), arg))

    if singlepage:
        gen = iter(singlepage)
    if ((FromName and ToName) == True):
        wikipedia.output(u'Do you want to move %s to %s?' % (oldName, newName))
        page = wikipedia.Page(wikipedia.getSite(), oldName)
        bot = MovePagesBot(None, prefix, delete, always)
        bot.moveOne(page,newName,delete)
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
