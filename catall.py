# -*- coding: utf-8 -*-
"""
Add or change categories on a number of pages. Usage:
catall.py name - goes through pages, starting at 'name'. Provides
the categories on the page and asks whether to change them. If no
starting name is provided, the bot starts at 'A'.

Options:
-onlynew : Only run on pages that do not yet have a category.
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2004
# (C) Filnik, 2008
#
# Distributed under the terms of the MIT license.
# 
__version__ = '$Id: catall.py,v 1.5 2008/01/12 12:49:25 filnik Exp$'
#

import wikipedia, sys

msg = {
    'en':u'Bot: Changing categories',
    'he':u'Bot: משנה קטגוריות',
    'fr':u'Bot: Change categories',
    'he':u'בוט: משנה קטגוריות',
    'ia':u'Bot: Alteration de categorias',
    'it':u'Bot: Cambio categorie',
    'ja':u'ロボットによる: カテゴリ変更',
    'lt':u'robotas: Keičiamos kategorijos',
    'nl':u'Bot: Verandering van categorieen',
    'pl':u'Bot: Zmiana kategorii',
    'pt':u'Bot: Categorizando',
    'sr':u'Bot: Ð˜Ð·Ð¼ÐµÐ½Ð° ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ñ˜Ð°',
    'zh':u'機器人: 更改分類',
    }

def choosecats(pagetext):
    chosen = []
    flag = False
    length = 1000
    textToPrint = """Give the new categories, one per line.
Empty line: if the first, don't change. Otherwise: Ready.
-: I made a mistake, let me start over.
?: Give the text of the page with GUI.
??: Give the text of the page in console.
xx: if the first, remove all categories and add no new.
q: quit."""
    wikipedia.output(textToPrint)
    while flag == False:
        choice = wikipedia.input(u"\nSo, what do you want to do?")
        if choice == "":
            flag = True
        elif choice == "-":
            chosen = choosecats(pagetext)
            flag = True
        elif choice == "?":
            import editarticle
            editor = editarticle.TextEditor()
            newtext = editor.edit(pagetext)
        elif choice == "??":
            wikipedia.output(pagetext[0:length])
            length = length+500 
        elif choice== "xx" and chosen == []:
            chosen = None
            flag = True
        elif choice == "q":
            wikipedia.output("quit...")
            sys.exit()
        else:
            chosen.append(choice)
    return chosen

def make_categories(page, list, site = None):
    if site is None:
        site = wikipedia.getSite()
    pllist = []
    for p in list:
        cattitle = "%s:%s" % (site.category_namespace(), p)
        pllist.append(wikipedia.Page(site,cattitle))
    page.put(wikipedia.replaceCategoryLinks(page.get(), pllist), comment = wikipedia.translate(site.lang, msg))

try:
    # This is a purely interactive robot. We set the delays lower.
    wikipedia.get_throttle.setDelay(5)
    wikipedia.put_throttle.setDelay(10)
    docorrections=True
    start = []

    for arg in wikipedia.handleArgs():
        if arg == '-onlynew':
            docorrections=False
        else:
            start.append(arg)

    if start == []:
        start = 'A'
    else:
        start = ' '.join(start)

    mysite = wikipedia.getSite()
    for p in mysite.allpages(start = start):
        try:
            text = p.get()
            cats = p.categories()
            if cats == []:
                wikipedia.output(u"========== %s ==========" % p.title())
                wikipedia.output("No categories")
                wikipedia.output("----------------------------------------")
                newcats=choosecats(text)
                if newcats != [] and newcats is not None:
                    make_categories(p, newcats, mysite)
            else:
                if docorrections:
                    wikipedia.output(u"========== %s ==========" % p.title())
                    for c in cats:
                        wikipedia.output(c.title())
                    wikipedia.output("----------------------------------------"
                    newcats=choosecats(text)
                    if newcats == None:
                        make_categories(p, [], mysite)
                    elif newcats != []:
                        make_categories(p, newcats, mysite)
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'%s is a redirect, skip...' % p.title())
            continue
finally:
    wikipedia.stopme()
