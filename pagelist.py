#coding: iso-8859-1
"""
This bot finds a collection of pages, starting with a single page. For
each page found, it checks all pages linked form or to the page, and asks
for each page linked from or to it, whether the user wants to include it.
This way, a collection of wikipages about a given subject can be found.

Arguments:
   -nodates  automatically skip all pages that are years or dates (years
             only work AD, dates only for certain languages)

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
X - add the page, but do not check links to and from it
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

datetable = {'nl':
             {
    'januari':{  'sl':'%d. januar',    'it':'%d gennaio',   'en':'January %d',   'de':'%d. Januar',    'fr':'%d janvier',   'af':'01-%02d', 'ca':'%d de gener',       'oc':'%d de geni%%C3%%A8r',  },
    'februari':{ 'sl':'%d. februar',   'it':'%d febbraio',  'en':'February %d',  'de':'%d. Februar',   'fr':'%d fevrier',   'af':'02-%02d', 'ca':'%d de febrer',      'oc':'%d de febri%%C3%%A8r', },
    'maart':{    'sl':'%d. marec',     'it':'%d marzo',     'en':'March %d',     'de':'%d. M&auml;rz', 'fr':'%d mars',      'af':'03-%02d', 'ca':'%d de_mar%%C3%%A7', 'oc':'%d de_mar%%C3%%A7',    },
    'april':{    'sl':'%d. april',     'it':'%d aprile',    'en':'April %d',     'de':'%d. April',     'fr':'%d avril',     'af':'04-%02d', 'ca':'%d d\'abril',       'oc':'%d d\'abril',          },
    'mei':{      'sl':'%d. maj',       'it':'%d maggio',    'en':'May %d',       'de':'%d. Mai',       'fr':'%d mai',       'af':'05-%02d', 'ca':'%d de maig',        'oc':'%d de mai',            },
    'juni':{     'sl':'%d. junij',     'it':'%d giugno',    'en':'June %d',      'de':'%d. Juni',      'fr':'%d juin',      'af':'06-%02d', 'ca':'%d de juny',        'oc':'%d de junh',           },
    'juli':{     'sl':'%d. julij',     'it':'%d luglio',    'en':'July %d',      'de':'%d. Juli',      'fr':'%d juillet',   'af':'07-%02d', 'ca':'%d de juliol',      'oc':'%d de julhet',         },
    'augustus':{ 'sl':'%d. avgust',    'it':'%d agosto',    'en':'August %d',    'de':'%d. August',    'fr':'%d aout',      'af':'08-%02d', 'ca':'%d d\'agost',       'oc':'%d d\'agost',          },
    'september':{'sl':'%d. september', 'it':'%d settembre', 'en':'September %d', 'de':'%d. September', 'fr':'%d septembre', 'af':'09-%02d', 'ca':'%d de setembre',    'oc':'%d de setembre',       },
    'oktober':{  'sl':'%d. oktober',   'it':'%d ottobre',   'en':'October %d',   'de':'%d. Oktober',   'fr':'%d octobre',   'af':'10-%02d', 'ca':'%d d\'octubre',     'oc':'%d d\'octobre',        },
    'november':{ 'sl':'%d. november',  'it':'%d novembre',  'en':'November %d',  'de':'%d. November',  'fr':'%d novembre',  'af':'11-%02d', 'ca':'%d de novembre',    'oc':'%d de novembre',       },
    'december':{ 'sl':'%d. december',  'it':'%d dicembre',  'en':'December %d',  'de':'%d. Dezember',  'fr':'%d decembre',  'af':'12-%02d', 'ca':'%d de desembre',    'oc':'%d de decembre',       },
    }}

yearBCfmt = {'da':'%d f.Kr.','de':'%d v. Chr.',
             'en':'%d BC','fr':'-%d','pl':'%d p.n.e.',
             'es':'%d adC','eo':'-%d','nl':'%d v. Chr.'}

def isdate(s):
    #is true iff s is a date or year
    result = False
    if datetable.has_key(wikipedia.mylang):
        dt='(\d+) (%s)' % ('|'.join(datetable[wikipedia.mylang].keys()))
        Rdate = re.compile(dt)
        m = Rdate.match(s)
        if m:
            result=True
    Ryear = re.compile('^\d+$')
    m = Ryear.match(s)
    if m:
        result=True
    return result


def asktoadd(pl):
    checkflag = 0 # we have not loaded this page yet
    if skipdates and isdate(pl.linkname()):
        return
    if not (pl in tocheck or pl in include or pl in exclude):
        print
        print("==%s==")%pl.linkname()
        while 1:
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
                print("x: Add the page, but do not check links to and from it")
                print("t: Give the beginning of the text of the page")
                print("a: Add another page")
                print("r: Remove a page already in the list")
                print("l: Give a list of the pages to check or to include")
            elif answer=='a':
                page = raw_input("Specify page to add:")
                if not (page in tocheck or page in include):
                    tocheck.append(wikipedia.PageLink(wikipedia.mylang,page))
            elif answer=='x':
                if pl.exists():
                    if pl.isRedirectPage():
                        print("Redirect page. Will be included normally.")
                        tocheck.append(pl)
                    else:
                        include.append(pl)
                else:
                    print("Page does not exist; not added.")
                    exclude.append(pl)
                break
            elif answer=='r':
                pagename = raw_input("Specify page to remove:")
                page = wikipedia.PageLink(wikipedia.mylang,pagename)
                exclude.append(page)
                for i in range(len(tocheck)-1, -1, -1):
                    if tocheck[i] == page:
                        del tocheck[i]
                for i in range(len(include)-1, -1, -1):
                    if include[i] == page:
                        del include[i]
            elif answer=='l':
                print("Number of pages still to check: %s")%len(tocheck)
                print("Number of pages checked and to be included: %s")%len(include)
                print("Number of pages not to include: %s")%len(exclude)
                print("Pages to be included:")
                print include
                print("Pages to be checked:")
                print tocheck
                print("==%s==")%pl.linkname()
            elif answer=='t':
                if checkflag == 0:
                    try:
                        print("==%s==")%pl.linkname()
                        print wikipedia.UnicodeToAsciiHtml(pl.get()[0:500])
                        ctoshow = 1000
                        checkflag = 1
                    except wikipedia.NoPage:
                        print("This page does not exist.")
                        checkflag = 2
                    except wikipedia.LockedPage:
                        print("Cannot load page.")
                        checkflag = 2
                    except wikipedia.IsRedirectPage,arg:
                        print("This is a redirect page. It redirects to: [[%s]].")%arg
                        checkflag = 2
                elif checkflag == 1:
                    print("==%s==")%pl.linkname()
                    print wikipedia.UnicodeToAsciiHtml(pl.get()[0:ctoshow])
                    ctoshow = ctoshow + 500
                elif checkflag == 2:
                    print("Unable to show the text of this page.")
            else:
                print("Not understood.")


tocheck = []
include = []
exclude = []
skipdates = False

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg=='-nodate':
        skipdates=True
    else:
        tocheck.append(wikipedia.PageLink(wikipedia.mylang,arg))

if tocheck == []:
    answer = raw_input("Which page to start with? ")
    tocheck.append(wikipedia.PageLink(wikipedia.mylang,answer))

while tocheck <> []:
    pg = tocheck[0]
    tocheck = tocheck[1:]
    if pg.exists():
        if pg.isRedirectPage():
            exclude.append(pg)
            new = wikipedia.PageLink(wikipedia.mylang,str(pg.getRedirectTo()))
            if not (new in tocheck or new in include or new in exclude):
                tocheck.append(new)
        else:
            include.append(pg)
            for new in pg.links():
                asktoadd(wikipedia.PageLink(wikipedia.mylang,new))
            for new in wikipedia.getReferences(pg):
                asktoadd(wikipedia.PageLink(wikipedia.mylang,new))
    else:
        exclude.append(pg)
        for new in wikipedia.getReferences(pg):
            asktoadd(wikipedia.PageLink(wikipedia.mylang,new))
    print

include.sort()
print
print("Collection of pages complete.")
print("=============================")
for page in include:
    print page


 
