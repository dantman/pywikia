"""
Library to work with category pages on Wikipedia
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
# 
__version__ = '$Id$'
#
import wikipedia

class _CatLink(wikipedia.PageLink):
    def catlist(self, recurse = 0):
        import re
        Rtitle = re.compile('title=\"([^\"]*)\"')
        ns = wikipedia.family.category_namespaces(wikipedia.mylang)
        state = 0
        catsdone = []
        catstodo = [self]
        pages = []
        while catstodo:
            cat = catstodo.pop()
            catsdone.append(cat)
            txt = wikipedia.getPage(cat.code(), cat.urlname(), do_edit = 0)
            ibegin = txt.index('<div id="content">')
            iend = txt.index('<div id="catlinks">')
            txt = txt[ibegin:iend]
            for title in Rtitle.findall(txt):
                if state == 0:
                    for ins in ns:
                        if title.startswith(ins):
                            state = 1
                            break
                if state == 1:
                    for ins in ns:
                        if title.startswith(ins):
                            break
                    else:
                        state = 2
                if state == 1:
                    ncat = _CatLink(self.code(), title)
                    if recurse and ncat not in catsdone:
                        catstodo.append(ncat)
                elif state == 2:
                    npage = wikipedia.PageLink(self.code(), title)
                    pages.append(npage)
        return pages
    
def CatLink(s):
    ns = wikipedia.family.category_namespaces(wikipedia.mylang)[0]
    return _CatLink(wikipedia.mylang, "%s:%s"%(ns, s))

def test():
    pl=CatLink('Biologie')
    
    print pl.catlist(recurse = 1)

if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        else:
            print "Ignored argument", arg
    test()
