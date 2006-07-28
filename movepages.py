#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot page moves to another title. Special Wikibooks-like pages.

Command-line arguments:

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".
                   
    -prefix        Automatic move pages in category with prefix name of the pages.
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
    'pt': u'Página movida por bot',
    }

def Movepages(page, deletedPages):
    pagetitle = page.title()
    wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
    ask = wikipedia.input('What do you do: (c)hange page name, (n)ext page or (q)uit?')
    if ask == 'c':
        pagemove = wikipedia.input(u'New page name:')
        titleroot = wikipedia.Page(wikipedia.getSite(), pagetitle)
        msg = wikipedia.translate(wikipedia.getSite(), comment)
        titleroot.move(pagemove, msg)
        wikipedia.output('Page %s move successful to %s.' % (pagetitle, pagemove))
        if deletedPages == True:
            pagedel = wikipedia.Page(wikipedia.getSite(), pagetitle)
            pagedel.delete(pagetitle)
        else:
            wikipedia.output('Do you need sysop right.')
    elif ask == 'n':
        pass
    elif ask == 'q':
        sys.exit()
    else:
        wikipedia.output('Input certain code.')
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
    else:
        wikipedia.output('Do you need sysop right.')

def main():
    categoryName = None
    singlePageTitle = []
    referredPageTitle = None
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
            elif arg.startswith('-prefix:'):
                if len(arg) == 8:
                    prefixPageTitle = wikipedia.input(u'Enter the prefix name of the pages in category: ')
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

    elif prefixPageTitle:
        categoryName = wikipedia.input('Category:')
        cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryName)
        gen = pagegenerators.CategorizedPageGenerator(cat)
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
