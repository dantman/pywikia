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

    -start         Work on all pages on the home wiki, starting at the named page.
                   
    -new           Work on the most recent new pages on the wiki.

    -from -to      The page to move from and the page to move to.

    -del           Argument can be given also together with other arguments,
                   its functionality is delete old page that was moved.
                   For example: "movepages.py pagetitle -del".

    -prefix        Move pages by adding a namespace prefix to the names of the pages.
                   (Will remove the old namespace prefix if any)
                   Argument can also be given as "-prefix:namespace:".

    -always        Don't prompt to make changes, just do them.

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

summary={
    'ar': u'نقل الصفحة بواسطة البوت',
    'en': u'Pagemove by bot',
    'de': u'Seite durch Bot verschoben',
    'el': u'Μετακίνηση σελίδων με bot',
    'fr': u'Page renommée par bot',
    'he': u'העברת דף באמצעות בוט',
    'nl': u'Paginatitel gewijzigd door robot',
    'pl': u'Przeniesienie artykułu przez robota',
    'pt': u'Página movida por bot',
}

deletesummary={
    'ar': u'حذف الصفحة بواسطة البوت',
    'en': u'Delete page by bot',
    'de': u'Seite durch Bot gelöscht',
    'el': u'Διαγραφή σελίδων με bot',
    'fr': u'Page supprimée par bot',
    'nl': u'Pagina verwijderd door robot',
    'pl': u'Usunięcie artykułu przez robota',
    'pt': u'Página apagada por bot',
}

class MovePagesBot:
    def __init__(self, generator, addprefix, delete, always):
        self.generator = generator
        self.addprefix = addprefix
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
            wikipedia.output(u'Page %s does not exist!' % page.title())
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
        except wikipedia.LockedPage:
            wikipedia.output(u'Page %s is locked!' % page.title())
            
    def treat(self,page):
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"% page.title())
        pagetitle = page.titleWithoutNamespace()
        namesp = page.site().namespace(page.namespace())
        if self.appendAll == True:
            pagemove = (u'%s%s%s' % (self.pagestart, pagetitle, self.pageend))
            if self.noNamespace == False and namesp:
                pagemove = (u'%s:%s' % (namesp, pagemove))
        elif self.regexAll == True:
            pagemove = self.regex.sub(self.replacePattern, pagetitle)
            if self.noNamespace == False and namesp:
                pagemove = (u'%s:%s' % (namesp, pagemove))
        if self.addprefix:
            pagemove = (u'%s%s' % (self.addprefix, pagetitle))
        if self.addprefix or self.appendAll == True or self.regexAll == True:
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
        else:
            wikipedia.output(u'What do you want to do:') 
            ask = wikipedia.input(u'(c)hange page name, (a)ppend to page name, use a (r)egular expression, (n)ext page or (q)uit?')
            if ask in ['c', 'C']:
                pagemove = wikipedia.input(u'New page name:')
                self.moveOne(page,pagemove,self.delete)
            elif ask in ['a', 'A']:
                self.pagestart = wikipedia.input(u'Append This to the start:')
                self.pageend = wikipedia.input(u'Append This to the end:')
                pagemove = (u'%s%s%s' % (self.pagestart, pagetitle, self.pageend))
                if namesp:
                    ask2 = wikipedia.input(u'Do you want to remove the namespace prefix "%s:"? [(Y)es, (N)o]'% namesp)
                    if ask2 in ['y', 'Y']:
                        noNamespace = True
                    else:
                        pagemove = (u'%s:%s' % (namesp, pagemove))
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
            elif ask in ['r', 'R']:
                searchPattern = wikipedia.input(u'Enter the search pattern:')
                self.replacePattern = wikipedia.input(u'Enter the replace pattern:')
                self.regex=re.compile(searchPattern)
                if page.title() == page.titleWithoutNamespace():
                    pagemove = self.regex.sub(self.replacePattern, page.title())
                else:                                             
                    ask2 = wikipedia.input(u'Do you want to remove the namespace prefix "%s:"? [(Y)es, (N)o]'% namesp)
                    if ask2 in ['y', 'Y']:
                        pagemove = self.regex.sub(self.replacePattern, page.titleWithoutNamespace())
                        noNamespace = True
                    else:                                             
                        pagemove = self.regex.sub(self.replacePattern, page.title())
                ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o, (A)ll, (Q)uit]' % pagemove)
                if ask2 in ['y', 'Y']:
                    self.moveOne(page,pagemove,self.delete)
                elif ask2 in ['a', 'A']:
                    self.regexAll = True
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

    def run(self):
        self.appendAll = False
        self.regexAll = False
        self.noNamespace = False
        for page in self.generator:
            self.treat(page)

def main():
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

    if ((FromName and ToName) == True):
        wikipedia.output(u'Do you move %s to %s!!' % (oldName, newName))
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

 	  	 
