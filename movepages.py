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

def Movepages(page, deletedPages):
    pagetitle = page.title()        
    wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
    try:
        getcontent = page.get()
    except wikipedia.LockedPage:
        wikipedia.output(u'Page is locked')
        pass
    except wikipedia.NoPage:
        wikipedia.output(u'Page not exist')
        pass
    
    ask = wikipedia.input('What do you do: (c)hange page name (a)ppend to page name, (n)ext page or (q)uit?')
    if ask in ['c', 'C']:
        pagemove = wikipedia.input(u'New page name:')
        titleroot = wikipedia.Page(wikipedia.getSite(), pagetitle)
        msg = wikipedia.translate(wikipedia.getSite(), comment)
        titleroot.move(pagemove, msg)
        wikipedia.output('Page %s move successful to %s.' % (pagetitle, pagemove))
        if deletedPages == True:
            pagedel = wikipedia.Page(wikipedia.getSite(), pagetitle)
    elif ask in ['a', 'A']:
        pagestart = wikipedia.input(u'Append This to the start:')
        pageend = wikipedia.input(u'Append This to the end:')
        pagemove = u'%s%s%s' % (pagestart,pagetitle,pageend)
        ask2 = wikipedia.input(u'Change the page title to "%s"? [(Y)es, (N)o]' % pagemove)
        if ask2 in ['y', 'Y']:
            titleroot = wikipedia.Page(wikipedia.getSite(), pagetitle)
            msg = wikipedia.translate(wikipedia.getSite(), comment)
            titleroot.move(pagemove, msg)
            wikipedia.output(u'Page %s move successful to %s.' % (pagetitle, pagemove))
            if deletedPages == True:
                pagedel = wikipedia.Page(wikipedia.getSite(), pagetitle)
                pagedel.delete(pagetitle)
    elif ask in ['n', 'N']:
        pass
    elif ask in ['q', 'Q']:
        sys.exit()
    else:
        wikipedia.output(u'Input certain code.')
        sys.exit()

def MovepageswithPrefix(page, prefixPageTitle, deletedPages):
    pagetitle = page.title()
    wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
    pagemove = ('%s%s' % (prefixPageTitle, pagetitle))
    titleroot = wikipedia.Page(wikipedia.getSite(), pagetitle)
    msg = wikipedia.translate(wikipedia.getSite(), comment)
    titleroot.move(pagemove, msg)
    wikipedia.output('Page %s move successful to %s.' % (pagetitle, pagemove))
    if deletedPages == True:
        pagedel = wikipedia.Page(wikipedia.getSite(), pagetitle)
        pagedel.delete(pagetitle)

def main():
    categoryName = None
    singlePageTitle = []
    referredPageTitle = None
    linkPage = None
    startpage = None
    prefixPageTitle = None
    deletedPages = False
    
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'movepages')
        if arg:
            if arg.startswith('-cat:'):
                if len(arg) == 5:
                    categoryName = wikipedia.input(u'Enter the category name:')
                else:
                    categoryName = arg[6:]
            elif arg.startswith('-ref:'):
                if len(arg) == 5:
                    referredPageTitle = wikipedia.input(u'Links to which page should be processed?')
                else:
                    referredPageTitle = arg[6:]
            elif arg.startswith('-link:'):
                if len(arg) == 6:
                    linkPage = wikipedia.input(u'Links from which page should be processed?')
                else:
                    linkPage = arg[6:]
            elif arg.startswith('-start:'):
                if len(arg) == 6:
                    startpage = wikipedia.input(u'Please enter the article to start then:')
                else:
                    startpage = arg[7:]
            elif arg.startswith('-prefix:'):
                if len(arg) == 8:
                    prefixPageTitle = wikipedia.input(u'Enter the prefix name of the pages in specific page: ')
                else:
                    prefixPageTitle = arg[9:]
            elif arg.startswith('-del'):
                deletedPages = True
            else:
                singlePageTitle.append(arg)

    if categoryName:
        cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryName)
        gen = pagegenerators.CategorizedPageGenerator(cat)
        generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        for page in generator: Movepages(page, deletedPages)

    elif referredPageTitle:
        referredPage = wikipedia.Page(wikipedia.getSite(), referredPageTitle)
        gen = pagegenerators.ReferringPageGenerator(referredPage)
        generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        for page in generator: Movepages(page, deletedPages)

    elif linkPage:
        linkingPage = wikipedia.Page(wikipedia.getSite(), linkPage)
        gen = pagegenerators.LinkedPageGenerator(linkingPage)
        generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        for page in generator: Movepages(page, deletedPages)

    elif startpage:
        start = wikipedia.Page(wikipedia.getSite(), startpage)
        gen = pagegenerators.AllpagesPageGenerator(startpage)
        for page in gen: Movepages(page, deletedPages)

    elif prefixPageTitle:
        listpageTitle = wikipedia.input(u'List of pages:')
        listpage = wikipedia.Page(wikipedia.getSite(), listpageTitle)
        gen = pagegenerators.LinkedPageGenerator(listpage)
        generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        for page in generator: MovepageswithPrefix(page, prefixPageTitle, deletedPages)
    
    else:
        singlePageTitle = ' '.join(singlePageTitle)
        if not singlePageTitle:
            singlePageTitle = wikipedia.input(u'Which page to move:')
        singlePage = wikipedia.Page(wikipedia.getSite(), singlePageTitle)
        Movepages(singlePage, deletedPages)

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
