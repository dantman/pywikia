# -*- coding: cp1252 -*-
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
# Distribute under the terms of the PSF license.
# 
__version__ = '$Id$'
#

import wikipedia,sys

# This is a purely interactive robot. We set the delays lower.
wikipedia.get_throttle.setDelay(5)
wikipedia.put_throttle.setDelay(10)

msg={
    'en': 'Changing categories',
    'nl': 'Verandering van categorieen'
    }

def choosecats(pagetext):
    chosen=[]
    flag=False
    length=1000
    print ("Give the new categories, one per line.")
    print ("Empty line: if the first, don't change. Otherwise: Ready.")
    print ("-: I made a mistake, let me start over.")
    print ("?: Give (more of) the text of the page.")
    print ("xx: if the first, remove all categories and add no nwe.")
    while flag == False:
        choice=raw_input("? ")
        if choice=="":
            flag=True
        elif choice=="-":
            chosen=choosecats(pagetext)
            flag=True
        elif choice=="?":
            wikipedia.output(pagetext[0:length])
            length = length+500
        elif choice=="xx" and chosen==[]:
            chosen = None
            flag=True
        else:
            chosen.append(choice)
    return chosen

def make_categories(page,list):
    pllist=[]
    for p in list:
        cattitle="%s:%s" % (wikipedia.family.category_namespace(wikipedia.mylang), p)
        pllist.append(wikipedia.PageLink(wikipedia.mylang,cattitle))
    page.put(wikipedia.replaceCategoryLinks(page.get(), pllist), comment = wikipedia.translate(wikipedia.mylang, msg))

docorrections=True
start=[]

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if arg == '-onlynew':
            docorrections=False
        else:
            start.append(arg)

if start == []:
    start='A'
else:
    start=' '.join(start)

for p in wikipedia.allpages(start = start):
    try:
        text=p.get()
        cats=p.categories()
        if cats == []:
            wikipedia.output("========== %s ==========" % p.linkname())
            print "No categories"
            print "----------------------------------------"
            newcats=choosecats(text)
            if newcats <> [] and newcats <> None:
                make_categories(p,newcats)
        else:
            if docorrections:
                wikipedia.output("========== %s ==========" % p.linkname())
                for c in cats:
                    print c.linkname()
                print "----------------------------------------"
                newcats=choosecats(text)
                if newcats == None:
                    make_categories(p,[])
                elif newcats <> []:
                    make_categories(p,newcats)
    except wikipedia.IsRedirectPage:
        pass
