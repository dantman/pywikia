#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot page moves to another title. Special Wikibooks-like pages.

Command-line arguments:

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

    -link          Work on all pages that are linked from a certain page.
                   Argument can also be given as "-link:linkingpagetitle".

    -start         Work on all pages on the home wiki, starting at the named page.
                   
    -prefix        Automatic move pages in specific page with prefix name of the pages.
                   Argument can also be given as "-prefix:Python/Pywikipediabot/".

    -from -to      The page to move from and the page to move to.

    -new           Work on the most recent new pages on the wiki.

    -del           Argument can be given also together with other arguments,
                   its functionality is delete old page that was moved.
                   For example: "movepages.py Helen_Keller -del".

Single pages use: movepages.py Helen_Keller

"""
#
# (C) Leonardo Gregianin, 2006
#
# Distributed under the terms of the MIT license.
#

__version__='$Id$'

import wikipedia, pagegenerators, catlib
import sys

comment={
    'en': u'Pagemove by bot',
    'he': u'העברת דף באמצעות בוט',
    'pt': u'Página movida por bot',
    }

deletecomment={
    'en': u'Delete page by bot',
    'pt': u'Página apagada por bot',
    }

class MovePagesWithPrefix:
    def __init__(self, generator, prefix, delete):
        self.generator = generator
        self.prefix = prefix
        self.delete = delete

    def PrefixMove(self, page, prefix, delete):
        pagemove = wikipedia.output(u'%s%s' % (prefix, page))
        titleroot = wikipedia.Page(wikipedia.getSite(), page)
        msg = wikipedia.translate(wikipedia.getSite(), comment)
        titleroot.move(pagemove, msg, throttle=True)
        if delete == True:
            pagedel = wikipedia.Page(wikipedia.getSite(), page)
            deletemsg = wikipedia.translate(wikipedia.getSite(), deletecomment)
            pagedel.delete(page, deletemsg)

    def run(self):
        for page in self.generator:
            try:
                pagetitle = page.title()
                wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
                self.PrefixMove(page, prefix, self.delete)
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s does not exist?!' % page.title())
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
            except wikipedia.LockedPage:
                wikipedia.output(u'Page %s is locked?!' % page.title())

class MovePagesBot:
    def __init__(self, generator, delete):
        self.generator = generator
        self.delete = delete

    def ChangePageName(self, page, delete):
        pagemove = wikipedia.input(u'New page name:')
        titleroot = wikipedia.Page(wikipedia.getSite(), pagemove)
        msg = wikipedia.translate(wikipedia.getSite(), comment)
        titleroot.move(pagemove, msg, throttle=True)
        if delete == True:
            pagedel = wikipedia.Page(wikipedia.getSite(), page)
            deletemsg = wikipedia.translate(wikipedia.getSite(), deletecomment)
            pagedel.delete(page, deletemsg)
            
    def AppendPageName(self, page, delete):
        pagestart = wikipedia.input(u'Append This to the start:')
        pageend = wikipedia.input(u'Append This to the end:')
        pagemove = (u'%s%s%s' % (pagestart, page, pageend))
        ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o]' % pagemove)
        if ask2 in ['y', 'Y']:
            titleroot = wikipedia.Page(wikipedia.getSite(), page.title())
            msg = wikipedia.translate(wikipedia.getSite(), comment)
            titleroot.move(pagemove, msg, throttle=True)
            if delete == True:
                pagedel = wikipedia.Page(wikipedia.getSite(), page)
                deletemsg = wikipedia.translate(wikipedia.getSite(), deletecomment)
                pagedel.delete(page, deletemsg)

    def run(self):
        for page in self.generator:
            try:
                pagetitle = page.title()
                wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
                ask = wikipedia.input('What do you do: (c)hange page name, (a)ppend to page name, (n)ext page or (q)uit?')
                if ask in ['c', 'C']:
                    self.ChangePageName(page, self.delete)
                elif ask in ['a', 'A']:
                    self.AppendPageName(page, self.delete)
                elif ask in ['n', 'N']:
                    pass
                elif ask in ['q', 'Q']:
                    sys.exit()
                else:
                    wikipedia.output(u'Input certain code.')
                    self.run()
            except wikipedia.NoPage:
                wikipedia.output('Page %s does not exist?!' % page.title())
            except wikipedia.IsRedirectPage:
                wikipedia.output('Page %s is a redirect; skipping.' % page.title())
            except wikipedia.LockedPage:
                wikipedia.output('Page %s is locked?!' % page.title())

def main():
    singlepage = []
    gen = cat = ref = link = start = prefix = None
    FromName = ToName = None
    delete = False
    
    for arg in wikipedia.handleArgs():
        if arg.startswith('-cat:'):
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s'%arg[5:])
            gen = pagegenerators.CategorizedPageGenerator(cat)
        elif arg.startswith('-ref:'):
            ref = wikipedia.Page(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.ReferringPageGenerator(ref)
        elif arg.startswith('-link:'):
            link = wikipedia.Page(wikipedia.getSite(), arg[6:])
            gen = pagegenerators.LinkedPageGenerator(link)
        elif arg.startswith('-start:'):
            start = wikipedia.Page(wikipedia.getSite(),arg[7:])
            gen = pagegenerators.AllpagesPageGenerator(start.titleWithoutNamespace(),namespace=start.namespace())
        elif arg.startswith('-new'):
            if not number:
                number = config.special_page_limit
            gen = pagegenerators.NewpagesPageGenerator(number)
        elif arg == '-del':
            delete = True
        elif arg.startswith('-from:'):
            oldName = arg[len('-from:'):]
            FromName = True
        elif arg.startswith('-to:'):
            newName = arg[len('-to:'):]
            ToName = True
        elif arg.startswith('-prefix:'):
            prefix = wikipedia.Page(wikipedia.getSite(), arg[8:])
            listpageTitle = wikipedia.input(u'List of pages:')
            listpage = wikipedia.Page(wikipedia.getSite(), listpageTitle)
            gen = pagegenerators.LinkedPageGenerator(listpage)
            preloadingGen = pagegenerators.PreloadingGenerator(gen)
            bot = MovePagesWithPrefix(preloadingGen, prefix, delete)
            bot.run()
        else:
            singlepage.append(arg)

    if singlepage:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(singlepage))
        gen = iter([page])
    elif ((FromName and ToName) == True):
        wikipedia.output(u'Do you will move %s to %s' % (oldName, newName))
        oldName = wikipedia.Page(wikipedia.getSite(), newName)
        msg = wikipedia.setAction(comment)
        oldName.move(newName, msg, throttle=True)
        if delete == True:
            pagedel = wikipedia.Page(wikipedia.getSite(), page)
            deletemsg = wikipedia.setAction(deletecomment)
            pagedel.delete(page, deletemsg)
    else:
        wikipedia.showHelp('movepages')
    if gen:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = MovePagesBot(preloadingGen, delete)
        bot.run()
                
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
