#coding: iso-8859-1
"""
This bot finds a collection of pages, starting with a single page. For
each page found, it checks all pages linked form or to the page, and asks
for each page linked from or to it, whether the user wants to include it.
This way, a collection of wikipages about a given subject can be found.

Arguments understood by all bots:
   -lang:XX  set your home wikipedia to XX instead of the one given in
             username.dat

Any other argument is taken as a page that at least has to be in the set.
Note that if a page has spaces in the title, you need to specify them
with _'s. A collection of pages about World War II would thus be gotten
with pagelist.py World_War_II.

When running the bot, you will get one by one a number by pages. You can
choose:
Y(es) - include the page
N(o) - do not include the page or
I(gnore) - do not include the page, but if you meet it again, ask again.
Other possiblities:
A(dd) - add another page, which may have been one that was included before
R(emove) - remove a page that is already in the list
L(ist) - show current list of pages to include or to check
"""
#
# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#
#
import sys, copy, re

import wikipedia

def asktoadd(pl):
    if not (pl in tocheck or pl in include or pl in exclude):
        while 1:
            print("%s")%pl
            answer = raw_input("y(es)/n(o)/i(gnore)/(o)ther options? ")
            if answer=='y':
                tocheck.append(pl)
                break
            elif answer=='n':
                exclude.append(pl)
                break
            elif answer=='i':
                break
            elif answer=='o':
                print("a: Add another page")
                print("r: Remove a page already in the list")
                print("l: Give a list of the pages to check or to include")
            elif answer=='s':
                save()
            elif answer=='a':
                page = raw_input("Specify page to add:")
                if not (page in tocheck or page in include):
                    tocheck.append(page)
            elif answer=='r':
                page = raw_input("Specify page to remove:")
                exclude.append(wikipedia.PageLink(wikipedia.mylang,page).linkname())
                for i in range(len(tocheck)-1, -1, -1):
                    if tocheck[i] == wikipedia.PageLink(wikipedia.mylang,page).linkname():
                        del tocheck[i]
                for i in range(len(include)-1, -1, -1):
                    if include[i] == wikipedia.PageLink(wikipedia.mylang,page).linkname():
                        del include[i]
            elif answer=='l':
                print('Number of pages still to check: %s')%len(tocheck)
                print('Number of pages checked and to be included: %s')%len(include)
                print('Number of pages not to include: %s')%len(exclude)
                print('Pages to be included:')
                print include
                print('Pages to be checked:')
                print tocheck

tocheck = []
include = []
exclude = []

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        tocheck.append(arg)

if tocheck == []:
    answer = raw_input("Which page to start with? ")
    tocheck.appen(answer)

while tocheck <> []:
    pg = wikipedia.PageLink(wikipedia.mylang,tocheck[0])
    pname = pg.linkname()
    tocheck = tocheck[1:]
    if pg.exists():
        if pg.isRedirectPage():
            exclude.append(pname)
            new = wikipedia.PageLink(wikipedia.mylang,str(pg.getRedirectTo())).linkname()
            if not (new in tocheck or new in include or new in exclude):
                tocheck.append(new)
        else:
            include.append(pname)
            for new in pg.links():
                asktoadd(wikipedia.PageLink(wikipedia.mylang,new).linkname())
            for new in wikipedia.getReferences(pg):
                asktoadd(wikipedia.PageLink(wikipedia.mylang,new).linkname())
    else:
        exclude.append(pname)
        for new in wikipedia.getReferences(pg):
            asktoadd(wikipedia.PageLink(wikipedia.mylang,new).linkname())
    print

include.sort()
print
print("Collection of pages complete.")
print("=============================")
for page in include:
    print page


 
