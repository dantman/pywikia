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
    #returns a list of the titles of all subcategories and all articles in this category
    def catlist(self, recurse = 0):
        import re
        Rtitle = re.compile('title=\"([^\"]*)\"')
        ns = wikipedia.family.category_namespaces(wikipedia.mylang)
        catsdone = []
        catstodo = [self]
        pages = []
        while catstodo:
            cat = catstodo.pop()
            catsdone.append(cat)
            txt = wikipedia.getPage(cat.code(), cat.urlname(), do_edit = 0)
            # index where subcategory listing begins
            # this only works for the current version of the MonoBook skin
            ibegin = txt.index('<br style="clear:both;" />')
            # index where article listing ends
            iend = txt.index('<!-- end content -->')
            txt = txt[ibegin:iend]
            for title in Rtitle.findall(txt):
                # try different possibilities for namespaces (first letter lowercase, English 'category')
                for ins in ns:
                    # if the current link points at a subcategory page
                    if title.startswith(ins + ':'):
                        ncat = _CatLink(self.code(), title)
                        if recurse and ncat not in catsdone:
                            catstodo.append(ncat)
                pages.append(title)
        # TODO: filter duplicate results
        return pages
    
    #returns a list of all subcategories in this category
    def subcategories(self, recurse = 0):
        ns = wikipedia.family.category_namespaces(wikipedia.mylang)
        subcats = []
        for title in self.catlist(recurse):
            for ins in ns:
                # if the current link points at a subcategory page
                if title.startswith(ins + ':'):
                    ncat = _CatLink(self.code(), title)
                    subcats.append(ncat)
        return subcats
    
    #returns a list of all articles in this category
    def articles(self, recurse = 0):
        articles = []
        titles = self.catlist(recurse)
        for title in titles:
            is_category = False
            for namespace in wikipedia.family.category_namespaces(wikipedia.mylang):
                # if the current link points to a subcategory
                if title.startswith(namespace + ':'):
                    is_category = True
            if not is_category:
                npage = wikipedia.PageLink(self.code(), title)
                articles.append(npage)
        return articles

     #TODO: create supercategories() function

def CatLink(s):
    ns = wikipedia.family.category_namespaces(wikipedia.mylang)[0]
    return _CatLink(wikipedia.mylang, "%s:%s"%(ns, s))

def test():
    pl=CatLink('Software')
    
    print pl.catlist(recurse = 0)

if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        else:
            print "Ignored argument", arg
    test()
