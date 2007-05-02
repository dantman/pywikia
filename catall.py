# -*- coding: utf-8 -*-
"""
Add or change categories on a number of pages. Usage: catall.py [option].

Provides the categories on the page and asks whether to change them.

Standard options:

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

Only catall options:

    -onlynew : Only run on pages that do not yet have a category.
               use in set the standards options.

    -uncat   : Give the list of articles in Special:Uncategorizedpages.
               use: catall.py -uncat

"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2004
#
# Distributed under the terms of the MIT license.
# 
__version__ = '$Id$'
#

import wikipedia, pagegenerators
import sys

# This is a purely interactive robot. We set the delays lower.
wikipedia.get_throttle.setDelay(5)
wikipedia.put_throttle.setDelay(10)

msg={
    'en':u'Bot: Changing categories',
    'he':u'Bot: משנה קטגוריות',
    'fr':u'Bot: Change categories',
    'ia':u'Bot: Alteration de categorias',
    'lt':u'robotas: Keičiamos kategorijos',
    'nl':u'Bot: Verandering van categorieen',
    'pl':u'Bot: Zmiana kategorii',
    'pt':u'Bot: Categorizando',
    'sr':u'Bot: Ð˜Ð·Ð¼ÐµÐ½Ð° ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ñ˜Ð°',
    }

def choosecats(pagetext):
    chosen=[]
    flag=False
    length=1000
    print ("Give the new categories, one per line.")
    print ("Empty line: if the first, don't change. Otherwise: Ready.")
    print ("-: I made a mistake, let me start over.")
    print ("e: Give the text of the page with graphical interface.")
    print ("??: Give the text of the page in console.") 
    print ("xx: if the first, remove all categories and add no new.")
    print ("x: quit.")
    while flag == False:
        choice=wikipedia.input(u"?")
        if choice=="":
            flag=True
        elif choice=="-":
            chosen=choosecats(pagetext)
            flag=True
        elif choice=="e":
            import editarticle
            editor = editarticle.TextEditor()
            newtext = editor.edit(pagetext)
        elif choice =="??":
            wikipedia.output(pagetext[0:length])
            length = length+500 
        elif choice=="xx" and chosen==[]:
            chosen = None
            flag=True
        else:
            chosen.append(choice)
    return chosen

def make_categories(page, list, site = None):
    if site is None:
        site = wikipedia.getSite()
    pllist=[]
    for p in list:
        cattitle="%s:%s" % (site.category_namespace(), p)
        pllist.append(wikipedia.Page(site,cattitle))
    page.put(wikipedia.replaceCategoryLinks(page.get(), pllist), comment = wikipedia.translate(site.lang, msg))

def main():
    docorrections=True
    gen = None
    mysite = wikipedia.getSite()

    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg == '-onlynew':
            docorrections=False
        if arg == '-uncat':
            generator = pagegenerators.UnCategorizedPageGenerator(number = 100)
            if generator:
                gen = generator
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
    if gen:
        try:
            for p in generator:
                try:
                    text=p.get()
                    cats=p.categories()
                    if cats == []:
                        wikipedia.output(u"========== %s ==========" % p.title())
                        print "No categories"
                        print "----------------------------------------"
                        newcats=choosecats(text)
                        if newcats != [] and newcats is not None:
                            make_categories(p, newcats, mysite)
                    else:
                        if docorrections:
                            wikipedia.output(u"========== %s ==========" % p.title())
                            for c in cats:
                                print c.title()
                            print "----------------------------------------"
                            newcats=choosecats(text)
                            if newcats == None:
                                make_categories(p, [], mysite)
                            elif newcats != []:
                                make_categories(p, newcats, mysite)
                except wikipedia.IsRedirectPage:
                    pass
                except wikipedia.NoPage:
                    pass
        finally:
            pass
        
    else:
        wikipedia.showHelp('catall')

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
