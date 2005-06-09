# -*- coding: UTF-8 -*-
"""
This bot takes as its argument (or, if no argument is given, asks for it), the
name of a new or existing category. It will then try to find new articles for
this category (pages linked to and from pages already in the category), asking
the user which pages to include and which not.

Arguments:
   -nodates  automatically skip all pages that are years or dates (years
             only work AD, dates only for certain languages)
   -forward  only check pages linked from pages already in the category,
             not pages linking to them. Is less precise but quite a bit
             faster.

When running the bot, you will get one by one a number by pages. You can
choose:
Y(es) - include the page
N(o) - do not include the page or
I(gnore) - do not include the page, but if you meet it again, ask again.
X - add the page, but do not check links to and from it
Other possiblities:
A(dd) - add another page, which may have been one that was included before
C(heck) - check links to and from the page, but do not add the page itself
R(emove) - remove a page that is already in the list
L(ist) - show current list of pages to include or to check
"""

# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#

import sys, codecs, re
import wikipedia, date, catlib

msg={
    'en':u'Creation or update of category:',
    'es':u'Creación o actualiza de la categoría:',
    'it':u'La creazione o laggiornamento di categoria:',
    'nl':u'Aanmaak of uitbreiding van categorie:',
    'pt':u'Criando ou atualizando categoria:',
    }

def rawtoclean(c):
    #Given the 'raw' category, provides the 'clean' category
    c2 = c.linkname().split('|')[0]
    return wikipedia.Page(mysite,c2)

def isdate(s):
    #returns true iff s is a date or year
    result = False
    if date.datetable.has_key(mysite):
        dt='(\d+) (%s)' % ('|'.join(date.datetable[wikipedia.mylang].keys()))
        Rdate = re.compile(dt)
        m = Rdate.match(s)
        if m:
            result = True
    Ryear = re.compile('^\d+$')
    m = Ryear.match(s)
    if m:
        result = True
    return result

def needcheck(pl):
    if checked.has_key(pl):
        return False
    if skipdates:
        if isdate(pl.linkname()):
            return False
    return True

def include(pl,checklinks=True,realinclude=True,linkterm=None):
    cl = checklinks
    if realinclude:
        try:
            text = pl.get()
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            cl = True
            pass
        else:
            cats = pl.categories()
            if not workingcat in cats:
                cats = pl.rawcategories()
                for c in cats:
                    if rawtoclean(c) in parentcats:
                        cats.remove(c)
                if linkterm:
                    pl.put(wikipedia.replaceCategoryLinks(text, cats + [wikipedia.Page(mysite,"%s|%s"%(workingcat.linkname(),linkterm))]))
                else:
                    pl.put(wikipedia.replaceCategoryLinks(text, cats + [workingcat]))
    if cl:
        if checkforward:
            try:
                pl.get()                
            except wikipedia.IsRedirectPage:
                pl2 = wikipedia.Page(mysite,pl.getRedirectTo())
                if needcheck(pl2):
                    tocheck.append(pl2)
                    checked[pl2]=pl2                
            except wikipedia.Error:
                pass
            else:
                for link in pl.links():
                    pl2 = wikipedia.Page(mysite,link)
                    if needcheck(pl2):
                        tocheck.append(pl2)
                        checked[pl2]=pl2
        if checkbackward:
            for refPage in pl.getReferences():
                if needcheck(refPage):
                    tocheck.append(refPage)
                    checked[refPage] = refPage

def exclude(pl,real_exclude=True):
    if real_exclude:
        excludefile.write('%s\n'%pl.linkname())

def asktoadd(pl):
    ctoshow = 500
    print
    print("==%s==")%pl.linkname()
    while 1:
        answer = raw_input("y(es)/n(o)/i(gnore)/(o)ther options? ")
        if answer=='y':
            include(pl)
            break
        if answer=='c':
            include(pl,realinclude=False)
            break
        if answer=='z':
            if pl.exists():
                if not pl.isRedirectPage():
                    linkterm = wikipedia.input(u"In what manner should it be alphabetized?")
                    include(pl,linkterm=linkterm)
                    break
            include(pl)
            break
        elif answer=='n':
            exclude(pl)
            break
        elif answer=='i':
            exclude(pl,real_exclude=False)
            break
        elif answer=='o':
            print("t: Give the beginning of the text of the page")
            print("z: Add under another title (as [[Category|Title]])")
            print("x: Add the page, but do not check links to and from it")
            print("c: Do not add the page, but do check links")
            print("a: Add another page")
            print("l: Give a list of the pages to check")
        elif answer=='a':
            pagetitle = raw_input("Specify page to add:")
            page=wikipedia.Page(wikipedia.mylang,pagetitle)
            if not page in checked.keys():
                include(page)
        elif answer=='x':
            if pl.exists():
                if pl.isRedirectPage():
                    print("Redirect page. Will be included normally.")
                    pl2=wikipedia.Page(mysite,pl.getRedirectTo())
                    checkprepare(pl2)
                else:
                    include(pl,checklinks=False)
            else:
                print("Page does not exist; not added.")
                exclude(pl,real_exclude=False)
            break
        elif answer=='l':
            print("Number of pages still to check: %s")%len(tocheck)
            print("Pages to be checked:")
            print tocheck
            print("==%s==")%pl.linkname()
        elif answer=='t':
            print("==%s==")%pl.linkname()
            try:
                wikipedia.output(pl.get(get_redirect=True)[0:ctoshow])
            except wikipedia.NoPage:
                print "Page does not exist."
            ctoshow += 500
        else:
            print("Not understood.")

try:
    checked = {}
    skipdates = False
    checkforward = True
    checkbackward = True
    workingcatname = []
    tocheck = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'makecat')
        if arg:
            if arg.startswith('-nodate'):
                skipdates = True
            elif arg.startswith('-forward'):
                checkbackward = False
            else:
                workingcatname.append(arg)

    if len(workingcatname) == 0:
        workingcatname = raw_input("Which page to start with? ")
    else:
        workingcatname = ' '.join(workingcatname)
    mysite = wikipedia.getSite()
    wikipedia.setAction(wikipedia.translate(mysite,msg) + ' ' + workingcatname)
    workingcat = catlib.CatLink(mysite,workingcatname)
    filename = 'category/' + wikipedia.UnicodeToAsciiHtml(workingcatname) + '_exclude.txt'
    try:
        f = codecs.open(filename, 'r', encoding = mysite.encoding())
        for line in f.readlines():
            # remove trailing newlines and carriage returns
            try:
                while line[-1] in ['\n', '\r']:
                    line = line[:-1]
            except IndexError:
                pass
            exclude(line,real_exclude=False)
            pl = wikipedia.Page(mysite,line)
            checked[pl] = pl
        f.close()
        excludefile = codecs.open(filename, 'a', encoding = mysite.encoding())
    except IOError:
        # File does not exist
        excludefile = codecs.open(filename, 'w', encoding = mysite.encoding())
    try:
        parentcats = workingcat.categories()
    except wikipedia.Error:
        parentcats = []
    list = workingcat.articles()
    if list:
        for pl in list:
            checked[pl]=pl
        wikipedia.getall(mysite,list)
        for pl in list:
            include(pl)
    else:
        wikipedia.output(u"Category %s does not exist or is empty. Which page to start with?"%workingcatname)
        answer = wikipedia.input(u"(Default is [[%s]]):"%workingcatname)
        if not answer:
            answer = workingcatname
        print answer
        pl = wikipedia.Page(mysite,answer)
        tocheck = []
        checked[pl] = pl
        include(pl)
    loaded = 0
    while tocheck:
        if loaded == 0:
            if len(tocheck) < 50:
                loaded = len(tocheck)
            else:
                loaded = 50
            wikipedia.getall(mysite,tocheck[:loaded])
        if not checkbackward:
            if not tocheck[0].exists():
                pass
            else:
                asktoadd(tocheck[0])
        else:
            asktoadd(tocheck[0])
        tocheck = tocheck[1:]
        loaded -= 1
finally:
    wikipedia.stopme()
    try:
        excludefile.close()
    except:
        pass
