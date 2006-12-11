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
#
# Distributed under the terms of the MIT license.
# 
__version__ = '$Id$'
#

import wikipedia,sys

# This is a purely interactive robot. We set the delays lower.
wikipedia.get_throttle.setDelay(5)
wikipedia.put_throttle.setDelay(10)

msg={
    'en': 'Bot: Changing categories',
    'he': 'Bot: משנה קטגוריות',
    'ia': 'Bot: Alteration de categorias',
    'nl': 'Bot: Verandering van categorieen',
    'pt': 'Bot: Categorizando',
    'sr': 'Bot: Ð˜Ð·Ð¼ÐµÐ½Ð° ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ñ˜Ð°',
    }

def choosecats(pagetext):
    chosen=[]
    flag=False
    length=1000
    print ("Give the new categories, one per line.")
    print ("Empty line: if the first, don't change. Otherwise: Ready.")
    print ("-: I made a mistake, let me start over.")
    print ("?: Give the text of the page with GUI.")
    print ("??: Give the text of the page in console.") 
    print ("xx: if the first, remove all categories and add no new.")
    while flag == False:
        choice=wikipedia.input(u"?")
        if choice=="":
            flag=True
        elif choice=="-":
            chosen=choosecats(pagetext)
            flag=True
        elif choice=="?":
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

docorrections=True
start=[]

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg, 'catall')
    if arg:
        if arg == '-onlynew':
            docorrections=False
        else:
            start.append(arg)

if start == []:
    start='A'
else:
    start=' '.join(start)

mysite = wikipedia.getSite()

try:
    for p in mysite.allpages(start = start):
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
finally:
    wikipedia.stopme()
