import sys,wikipedia,interwiki

def ReadWarnfile(fn):
    import re
    print "Parsing...."
    R=re.compile(r'WARNING: ([^\[]*):\[\[([^\[]+)\]\]([^\[]+)\[\[([^\[]+):([^\[]+)\]\]')
    f=open(fn)
    hints={}
    for line in f.readlines():
        m=R.search(line)
        if m:
            #print "DBG>",line
            if m.group(1)==wikipedia.mylang:
                #print m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
                if not hints.has_key(m.group(2)):
                    hints[m.group(2)]=[]
                #print m.group(3)
                if m.group(3) == ' links to incorrect ':
                    sign='-'
                else:
                    sign='+'
                try:
                    hints[m.group(2)].append((sign,wikipedia.PageLink(m.group(4),wikipedia.link2url(m.group(5),m.group(4)))))
                except wikipedia.Error:
                    print "DBG> Failed to add", line
                #print "DBG> %s : %s" % (m.group(2), hints[m.group(2)])
    f.close()
    k=hints.keys()
    k.sort()
    print "Fixing... %d pages" % len(k)
    for pagename in k:
        pl = wikipedia.PageLink(wikipedia.mylang, pagename)
        old={}
        for pl2 in pl.interwiki():
            old[pl2.code()] = pl2
        new={}
        new.update(old)
        for sign,pl2 in hints[pagename]:
            code = pl2.code()
            if sign == '+':
                new[code] = pl2
            elif sign == '-':
                try:
                    del new[code]
                except KeyError:
                    pass
            else:
                raise "Bug"
        mods, removing = interwiki.compareLanguages(old, new)
        if mods:
            print pl.asasciilink(),mods
            oldtext = pl.get()
            newtext = wikipedia.replaceLanguageLinks(oldtext, new)
            if 1:
                interwiki.showDiff(oldtext, newtext)
                status, reason, data = pl.put(newtext, comment='warnfile '+mods)
                if str(status) != '302':
                    print status, reason
            

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        else:
            ReadWarnfile(arg)
