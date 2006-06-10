#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Bot page moves to another title in category.

"""
#
# Distributed under the terms of the MIT license.
#

import wikipedia, pagegenerators, catlib

comment={
    'en': u'Pagemove by bot',
    'pt': u'Página movida por bot',
    }

def Movepages(page):
    try:
        wikipedia.output(u'\n>>> %s <<<<' % page.title())
        pagetitle = page.title()
        pagemove = wikipedia.input(u'Another title:')
        titleroot = wikipedia.Page(mysite, pagetitle)

        msg = wikipedia.translate(mysite, comment)
        titleroot.move(pagemove, msg)
    except:
        pass #ctrl-c: next page

def main():
    mysite = wikipedia.getSite()
    categoryname = wikipedia.input(u'Please enter the category name:')
    cat = catlib.Category(mysite, 'Category:%s' % categoryname)
    gen = pagegenerators.CategorizedPageGenerator(cat)
    generator = pagegenerators.PreloadingGenerator(gen, pageNumber = [])
        
    for page in generator:
        Movepages(page)

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
