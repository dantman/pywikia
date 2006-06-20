#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot page moves to another title. Special Wikibooks-like pages.

Command-line arguments:

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

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

def Movepages(page):
    try:
        mysite = wikipedia.getSite()
        pagetitle = page.title()
        wikipedia.output(u'\n>>>> %s <<<<' % pagetitle)
        pagemove = wikipedia.input(u'Another title:')
        titleroot = wikipedia.Page(mysite, pagetitle)
        msg = wikipedia.translate(mysite, comment)
        titleroot.move(pagemove, msg)

        # if titleroot don't have referred pages, delete.
        # pagedel = wikipedia.Page(mysite, pagetitle)
        # pagedel.delete(pagetitle)
        
    except:
        pass #ctrl-c: next page

def main():
    mysite = wikipedia.getSite()
    categoryName = None
    singlePageTitle = []
    referredPageTitle = None
    preTitle = None
    
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'movepages')
        if arg:
            if arg.startswith('-cat'):
                if len(arg) == 4:
                    categoryName = wikipedia.input(u'Enter the category name:')
                else:
                    categoryName = arg[5:]
            elif arg.startswith('-ref'):
                if len(arg) == 4:
                    referredPageTitle = wikipedia.input(u'Links to which page should be processed?')
                else:
                    referredPageTitle = arg[5:]
            else:
                singlePageTitle.append(arg)

    if categoryName:
        cat = catlib.Category(mysite, 'Category:%s' % categoryName)
        gen = pagegenerators.CategorizedPageGenerator(cat)
        generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        for page in generator: Movepages(page)

    elif referredPageTitle:
        referredPage = wikipedia.Page(mysite, referredPageTitle)
        generator = pagegenerators.ReferringPageGenerator(referredPage)
        for page in generator: Movepages(page)

    else:
        singlePageTitle = ' '.join(singlePageTitle)
        if not singlePageTitle:
            singlePageTitle = wikipedia.input(u'Which page to move:')
        singlePage = wikipedia.Page(mysite, singlePageTitle)
        Movepages(singlePage)

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
