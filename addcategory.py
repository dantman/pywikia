"""
A robot to mass-add a category to a list of pages.

Just run this robot without any arguments

"""
#
# (C) Rob W.W. Hooft, 2004
#
# Distribute under the terms of the PSF license.
# 
__version__ = '$Id$'
#
import sys, wikipedia, interwiki

def main():
    import re
    print "This bot has two modes: you can add a category link to all"
    print "pages mentioned in a List that is now in another wikipedia page"
    print "or you can add a category link to all pages that link to a"
    print "specific page. If you want the second, please give an empty"
    print "answer to the first question."
    listpage = raw_input('Wikipedia page with list of pages to change: ')
    if listpage:
        pl = wikipedia.PageLink(wikipedia.mylang, listpage)
        pagenames = pl.links()
    else:
        refpage = raw_input('Wikipedia page that is now linked to: ')
        pl = wikipedia.PageLink(wikipedia.mylang, refpage)
        pagenames = wikipedia.getReferences(pl)
    print "  ==> %d pages to process"%len(pagenames)
    print
    newcat = raw_input('Category to add (do not give namespace) : ')
    ns = wikipedia.family.category_namespaces(wikipedia.mylang)
    
    catpl = wikipedia.PageLink(wikipedia.mylang, ns[0]+':'+newcat.capitalize())
    print "Will add %s"%catpl.aslocallink()

    for nm in pagenames:
        pl2 = wikipedia.PageLink(wikipedia.mylang, nm)
        answer = ''
        while answer not in ('y','n'):
            answer = raw_input("%s [y/n] : "%(pl2.asasciilink()))
        if answer == 'y':
            cats = pl2.categories()
            print "Current categories: ",cats
            if catpl in cats:
                print "%s already has %s"%(pl.aslocallink(),catpl.aslocallink())
            else:
                cats.append(catpl)
                text = pl2.get()
                text = wikipedia.replaceCategoryLinks(text, cats)
                pl2.put(text, comment = catpl.aslocallink())

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
    main()
