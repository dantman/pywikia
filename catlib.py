# -*- coding: utf-8  -*-
"""
Library to work with category pages on Wikipedia
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2004
#
# Distributed under the terms of the MIT license.
# 
__version__ = '$Id$'
#
import re, time
import wikipedia

msg_created_for_renaming = {
    'de':u'Bot: Verschoben von %s. Autoren: %s',
    'en':u'Robot: Moved from %s. Authors: %s',
    'fr':u'Robot : déplacé depuis %s. Auteurs: %s',
    }

def isCatTitle(title, site):
    return ':' in title and title[:title.index(':')] in site.category_namespaces()

def unique(l):
    """Given a list of hashable object, return an alphabetized unique list.
    """
    l=dict.fromkeys(l).keys()
    l.sort()
    return l
    
class Category(wikipedia.Page):
    """Subclass of Page that has some special tricks that only work for
       category: pages"""

    def __init__(self, site, title = None, insite = None, tosite = None, sortKey = None):
        wikipedia.Page.__init__(self, site = site, title = title, insite = insite, tosite = tosite)
        self.sortKey = sortKey
        if self.namespace() != 14:
            raise ValueError(u'BUG: %s is not in the category namespace!' % title)

    def aslink(self):
        """
        A string representation in the form of a link. This method is different
        from Page.aslink() as the link will never have the form of an an
        interwiki link.
        """
        if self.sortKey:
            titleWithSortKey = '%s|%s' % (self.title(), self.sortKey)
        else:
            titleWithSortKey = self.title()
        return '[[%s]]' % titleWithSortKey

	
    def catlist(self, recurse = False, purge = False):
        """Cache result of make_catlist for a second call

           This should not be used outside of this module.
        """
        if purge:
            self._catlistT = self._make_catlist(recurse = recurse, purge = True)
        # if we don't have a cached version
        elif not hasattr(self, '_catlistT'):
            self._catlistT = self._make_catlist(recurse = recurse)
        return self._catlistT
            
    def _make_catlist(self, recurse = False, purge = False, site = None):
        """Make a list of all articles and categories that are in this
           category. If recurse is set to True, articles and subcategories
           of any subcategories are also retrieved.

           Returns non-unique, non-sorted lists of articles, subcategories and
           supercategories. The supercategory list only contains the
           supercategories of this category, regardless of the recurse argument.

           This should not be used outside of this module.
        """
        if site is None:
            site = self.site()
        import re
        if site.version() < "1.4":
            Rtitle = re.compile('title\s?=\s?\"([^\"]*)\"')
        else:
            Rtitle = re.compile('/wiki/\S* title\s?=\s?\"([^\"]*)\"')
        ns = site.category_namespaces()
        catsdone = []
        catstodo = [self]
        articles = []
        subcats = []
        supercats=[]
        # regular expression matching the "(next 200)" link
        RLinkToNextPage = re.compile('&amp;from=(.*?)" title="');
        
        while catstodo:
            cat = catstodo.pop()
            catsdone.append(cat)
            # if category list is split up into several pages, this variable
            # stores where the next list page should start
            startFromPage = None
            thisCatDone = False
            # This loop will run until all list pages of the current category
            # have been read. Note: supercategories are displayed equally on
            # each of the list pages, so we will care about them after this
            # loop.
            while not thisCatDone:
                path = site.get_address(cat.urlname())
                if startFromPage:
                    path += '&from=' + startFromPage
                if purge:
                    path += '&action=purge'
                if startFromPage:
                    wikipedia.output('Getting [[%s]] starting at %s...' % (cat.title(), startFromPage))
                else:
                    wikipedia.output('Getting [[%s]]...' % cat.title())
                txt = site.getUrl(path)             
                # save a copy of this text to find out self's supercategory.
                # if recurse is true, this function should only return self's
                # supercategory, not the ones of its subcats.
                self_txt = txt
                # index where subcategory listing begins
                # this only works for the current version of the MonoBook skin
                ibegin = txt.index('"clear:both;"')
                # index where article listing ends
                try:
                    iend = txt.index('<div id="catlinks">')
                except ValueError:
                    iend = txt.index('<!-- end content -->')
                txt = txt[ibegin:iend]
                for title in Rtitle.findall(txt):
                    if isCatTitle(title, self.site()):
                        ncat = Category(self.site(), title)
                        if recurse and ncat not in catsdone:
                            catstodo.append(ncat)
                        subcats.append(title)
                    else:
                        articles.append(title)
                # try to find a link to the next list page
                matchObj = RLinkToNextPage.search(txt)
                if matchObj:
                    startFromPage = matchObj.group(1)
                    wikipedia.output('There are more articles in %s.' % cat.title())
                else:
                    thisCatDone = True
        # get supercategories
        try:
            ibegin = self_txt.index('<div id="catlinks">')
            iend = self_txt.index('<!-- end content -->')
        except ValueError:
            # no supercategories found
            pass
        else:
            self_txt = self_txt[ibegin:iend]
            if self.site().version() < '1.5':
                # MediaWiki 1.4 has an unneeded space here
                Rsupercat = re.compile('title ="([^"]*)"')
            else:
                Rsupercat = re.compile('title="([^"]*)"')
            for title in Rsupercat.findall(self_txt):
                # There might be a link to Special:Categories we don't want
                if isCatTitle(title, self.site()):
                    supercats.append(title)
        return (articles, subcats, supercats)
    
    def subcategories(self, recurse = False):
        """Create a list of all subcategories of the current category.

           If recurse = True, also return subcategories of the subcategories.

           Returns a sorted, unique list of all subcategories.
        """
        subcats = []
        for title in self.catlist(recurse)[1]:
            ncat = Category(self.site(), title)
            subcats.append(ncat)
        return unique(subcats)
    
    #returns a list of all articles in this category
    def articles(self, recurse = False):
        """Create a list of all pages in the current category.

           If recurse = True, also return pages in all subcategories.

           Returns a sorted, unique list of all categories.
        """
        articles = []
        for title in self.catlist(recurse)[0]:
            npage = wikipedia.Page(self.site(), title)
            articles.append(npage)
        return unique(articles)

    def supercategories(self, recurse = False):
        """Create a list of all subcategories of the current category.

           If recurse = True, also return subcategories of the subcategories.

           Returns a sorted, unique list of all subcategories.
        """
        supercats = []
        for title in self.catlist(recurse)[2]:
            ncat = Category(self.site(), title)
            supercats.append(ncat)
        return unique(supercats)
    
    def isEmpty(self):
        # TODO: rename; naming conflict with Page.isEmpty
        (articles, subcats, supercats) = self.catlist(purge = True)
        return (articles == [] and subcats == [])
    
    def copyTo(self, catname):
        """
        Returns true if copying was successful, false if target page already
        existed.
        """
        catname = self.site().category_namespace() + ':' + catname
        targetCat = wikipedia.Page(self.site(), catname)
        if targetCat.exists():
            wikipedia.output('Target page %s already exists!' % targetCat.title())
            return False
        else:
            wikipedia.output('Moving text from %s to %s.' % (self.title(), targetCat.title()))
            authors = ', '.join(self.contributingUsers())
            creationSummary = wikipedia.translate(wikipedia.getSite(), msg_created_for_renaming) % (self.title(), authors)
            targetCat.put(self.get(), creationSummary)
            return True
    
#def Category(code, name):
#    """Factory method to create category link objects from the category name"""
#    # Standardized namespace
#    ns = wikipedia.getSite().category_namespaces()[0]
#    # Prepend it
#    return Category(code, "%s:%s" % (ns, name))

def change_category(article, oldCat, newCat, comment=None):
    """
    Given an article which is in category oldCat, moves it to
    category newCat. Moves subcategories of oldCat as well.
    oldCat and newCat should be Category objects.
    If newCat is None, the category will be removed.
    """
    cats = article.categories()
    site = article.site()
    removed = False
    # This loop will stop after the first occurence of the category was found
    # and replaced. There might also be cases where a category was inserted
    # twice in an article; the bot would then only replace the first occurence.
    for i in range(len(cats)):
        cat = cats[i]
        if cat == oldCat:
            sortKey = cat.sortKey
            if not newCat:
                cats = cats[:i] + cats[i+1:]
            else:
                newCat = Category(site, newCat.title(), sortKey = sortKey)
                cats = cats[:i] + [newCat] + cats[i+1:]
            text = article.get()
            text = wikipedia.replaceCategoryLinks(text, cats)
            article.put(text, comment)
	    return
    wikipedia.output(u'ERROR: %s is not in category %s!' % (article.aslink(), oldCat.title()))
    return


def test():
    site = wikipedia.getSite()
    
    pl=Category(site, 'Software')
    
    print pl.catlist(recurse = False)

    print pl.subcategories(recurse = False)

    print pl.articles(recurse = False)

if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'catlib')
        if arg:
            print "Ignored argument", arg
    test()
