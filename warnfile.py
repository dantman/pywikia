"""
A robot to implement backlinks from a treelang.log file without checking them
against the live wikipedia.

Just run this robot with the warnfile names as arguments:

Example:

   python warnfile.py -lang:es nl/warning_es.dat

"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
# 
__version__ = '$Id$'
#
import sys, wikipedia, interwiki

def ReadWarnfile(fn):
    import re
    print "Parsing...."
    R=re.compile(r'WARNING: ([^\[]*):\[\[([^\[]+)\]\]([^\[]+)\[\[([^\[]+):([^\[]+)\]\]')
    f=open(fn)
    hints={}
    mysite=wikipedia.getSite()
    for line in f.readlines():
        m=R.search(line)
        if m:
            #print "DBG>",line
            if m.group(1)==mysite.lang:
                print m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
                if not hints.has_key(m.group(2)):
                    hints[m.group(2)]=[]
                #print m.group(3)
                if m.group(3) == ' links to incorrect ':
                    sign='-'
                else:
                    sign='+'
                try:
                    if ':' in m.group(4):
                        family, lang = m.group(4).split(':')
                        thesite = wikipedia.getSite(code=lang, fam=family)
                    else:
                        thesite = mysite.getSite(code = m.group(4))
                    hints[m.group(2)].append((sign,wikipedia.PageLink(thesite,wikipedia.link2url(m.group(5),site = thesite))))
                except wikipedia.Error:
                    print "DBG> Failed to add", line
                #print "DBG> %s : %s" % (m.group(2), hints[m.group(2)])
    f.close()
    k=hints.keys()
    k.sort()
    print "Fixing... %d pages" % len(k)
    for pagename in k:
        pl = wikipedia.PageLink(mysite, pagename)
        old={}
        try:
           for pl2 in pl.interwiki():
              old[pl2.site()] = pl2
        except wikipedia.IsRedirectPage:
           wikipedia.output("%s is a redirect page; not changing" % pl.aslink())
           continue
        except wikipedia.NoPage:
           wikipedia.output("Page %s not found; skipping" % pl.aslink())
           continue
        new={}
        new.update(old)
        for sign,pl2 in hints[pagename]:
            site = pl2.site()
            if sign == '+':
                new[site] = pl2
            elif sign == '-':
                try:
                    del new[site]
                except KeyError:
                    pass
            else:
                raise "Bug"
        mods, removing = interwiki.compareLanguages(old, new)
        if mods:
            wikipedia.output(pl.aslink() + mods)
            oldtext = pl.get()
            newtext = wikipedia.replaceLanguageLinks(oldtext, new)
            if 1:
                wikipedia.showDiff(oldtext, newtext)
                status, reason, data = pl.put(newtext, comment='warnfile '+mods)
                if str(status) != '302':
                    print status, reason
            

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            ReadWarnfile(arg)
