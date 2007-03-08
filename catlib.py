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
try:
    set # introduced in Python 2.4: faster and future
except NameError:
    # fallback solution for Python 2.3
    from sets import Set as set

msg_created_for_renaming = {
    'de':u'Bot: Verschoben von %s. Autoren: %s',
    'en':u'Robot: Moved from %s. Authors: %s',
    'ia':u'Robot: Transferite de %s. Autores: %s',
    'fr':u'Robot : déplacé depuis %s. Auteurs: %s',
    'he':u'רובוט: הועבר מהשם %s. מחברים: %s',
    'pl':u'Robot przenosi z %s. Autorzy: %s',
    'pt':u'Bot: Movido de %s. Autor: %s',
    }

# some constants that are used internally
ARTICLE = 0
SUBCATEGORY = 1
SUPERCATEGORY = 2

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

    def __init__(self, site, title = None, insite = None, sortKey = None):
        wikipedia.Page.__init__(self, site = site, title = title, insite = insite)
        self.sortKey = sortKey
        if self.namespace() != 14:
            raise ValueError(u'BUG: %s is not in the category namespace!' % title)
        self.completelyCached = False
        self.articleCache = []
        self.subcatCache = []
        self.supercatCache = []

    def aslink(self, forceInterwiki = False):
        """
        A string representation in the form of a link. This method is different
        from Page.aslink() as the sortkey may have to be included.
        """
        if self.sortKey:
            titleWithSortKey = '%s|%s' % (self.title(), self.sortKey)
        else:
            titleWithSortKey = self.title()
        if forceInterwiki or self.site() != wikipedia.getSite():
            if self.site().family != wikipedia.getSite().family:
                return '[[%s:%s:%s]]' % (self.site().family.name, self.site().lang, titleWithSortKey)
            else:
                return '[[%s:%s]]' % (self.site().lang, titleWithSortKey)
        else:
            return '[[%s]]' % titleWithSortKey

	
    def _getContentsAndSupercats(self, recurse = False, purge = False, startFrom = None):
        """
        Cache results of _parseCategory for a second call.

        Parameters are analogous to _parseCategory(). If purge is True,
        cached results will be discarded. If startFrom is used, nothing
        will be cached.

        This should not be used outside of this module.
        """
        if purge:
            self.completelyCached = False
        if self.completelyCached:
            for article in self.articleCache:
                yield ARTICLE, article
            for subcat in self.subcatCache:
                yield SUBCATEGORY, subcat
            for supercat in self.supercatCache:
                yield SUPERCATEGORY, supercat
        else:
            for type, title in self._parseCategory(recurse = recurse, purge = purge, startFrom = startFrom):
                if type == ARTICLE:
                    self.articleCache.append(title)
                elif type == SUBCATEGORY:
                    self.subcatCache.append(title)
                elif type == SUPERCATEGORY:
                    self.supercatCache.append(title)
                yield type, title
            if not startFrom:
                self.completelyCached = True

    def _parseCategory(self, recurse = False, purge = False, startFrom = None):
        """
        Yields all articles and subcategories that are in this category,
        as well as its supercategories. If recurse is set to True, articles
        and subcategories of any subcategories are also retrieved. If recurse
        is set to a number, the subcategories will be retrieved upto that
        level of recursion. Only the supercategories of the given category
        will be yielded, regardless of the recurse argument.

        Set purge to True to instruct MediaWiki not to serve a cached version.

        Set startFrom to a string which is the title of the page to start from.

        Yielded results are tuples in the form (type, title) where type is one
        of the constants ARTICLE, SUBCATEGORY and SUPERCATEGORY, and title is
        the title (with namespace) of the page or category.

        Note that results of this method need not be unique.

        This should not be used outside of this module.
        """
        if self.site().version() < "1.4":
            Rtitle = re.compile('title\s?=\s?\"([^\"]*)\"')
        elif self.site().version() < "1.8":
            Rtitle = re.compile('/\S*(?: title\s?=\s?)?\"([^\"]*)\"')
        else:
            Rtitle = re.compile('title\s?=\s?\"([^\"]*)\"\>\+?[^\<\+]')
        if self.site().version() < "1.8":
            Rsubcat = None
        else:
            Rsubcat = re.compile('CategoryTreeLabelCategory\"\s?href=\".+?\">(.+?)</a>')
        ns = self.site().category_namespaces()
        catsdone = []
        catstodo = [(self,recurse)]
        # regular expression matching the "(next 200)" link
        RLinkToNextPage = re.compile('&amp;from=(.*?)" title="');
        
        while catstodo:
            (cat,recurselevel) = catstodo.pop()
            if type(recurselevel) == type(1):
                newrecurselevel = recurselevel - 1
            else:
                newrecurselevel = recurselevel
            catsdone.append(cat)
            # if category list is split up into several pages, this variable
            # stores where the next list page should start
            currentPageOffset = startFrom
            thisCatDone = False
            # This loop will run until all list pages of the current category
            # have been read. Note: supercategories are displayed equally on
            # each of the list pages, so we will care about them after this
            # loop.
            while not thisCatDone:
                path = self.site().get_address(cat.urlname())
                if currentPageOffset:
                    path += '&from=' + currentPageOffset
                if purge:
                    path += '&action=purge'
                if currentPageOffset:
                    wikipedia.output('Getting [[%s]] starting at %s...' % (cat.title(), currentPageOffset))
                else:
                    wikipedia.output('Getting [[%s]]...' % cat.title())
                wikipedia.get_throttle()
                txt = self.site().getUrl(path)
                # save a copy of this text to find out self's supercategory.
                # if recurse is true, this function should only return self's
                # supercategory, not the ones of its subcats.
                self_txt = txt
                # index where subcategory listing begins
                # this only works for the current version of the MonoBook skin
                ibegin = txt.index('"clear:both;"')
                # index where article listing ends
                try:
                    iend = txt.index('<div class="printfooter">')
                except ValueError:
                    try:
                        iend = txt.index('<div id="catlinks">')
                    except ValueError:
                        iend = txt.index('<!-- end content -->')
                txt = txt[ibegin:iend]
                for title in Rtitle.findall(txt):
                    if title == self.title():
                        # This is only a link to "previous 200" or "next 200".
                        # Ignore it.
                        pass
                    # For MediaWiki versions where subcats look like articles
                    elif isCatTitle(title, self.site()):
                        ncat = Category(self.site(), title)
                        if recurselevel and ncat not in catsdone:
                            catstodo.append((ncat,newrecurselevel))
                        yield SUBCATEGORY, title
                    else:
                        yield ARTICLE, title
                if Rsubcat:
                    # For MediaWiki versions where subcats look differently
                    for titleWithoutNamespace in Rsubcat.findall(txt):
                        title = 'Category:%s' % titleWithoutNamespace
                        ncat = Category(self.site(), title)
                        if recurselevel and ncat not in catsdone:
                            catstodo.append((ncat,newrecurselevel))
                        yield SUBCATEGORY, title
                # try to find a link to the next list page
                matchObj = RLinkToNextPage.search(txt)
                if matchObj:
                    currentPageOffset = matchObj.group(1)
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
                    yield SUPERCATEGORY, title
    
    def subcategories(self, recurse = False):
        """
        Yields all subcategories of the current category.

        If recurse is True, also yields subcategories of the subcategories.
        If recurse is a number, also yields subcategories of subcategories,
        but only at most that number of levels deep (that is, recurse = 0 is
        equivalent to recurse = False, recurse = 1 gives subcategories and
        subcategories but no deeper, etcetera).

        Results a sorted (as sorted by MediaWiki), but need not be unique.
        """
        for type, title in self._getContentsAndSupercats(recurse):
            if type == SUBCATEGORY:
                yield Category(self.site(), title)

    def subcategoriesList(self, recurse = False):
        """
        Creates a list of all subcategories of the current category.

        If recurse is True, also return subcategories of the subcategories.
        Recurse can also be a number, as explained above.

        The elements of the returned list are sorted (as sorted by MediaWiki)
        and unique.
        """
        subcats = []
        for cat in self.subcategories(recurse):
            subcats.append(cat)
        return unique(subcats)

    def articles(self, recurse = False, startFrom = None):
        """
        Yields all articles of the current category.

        If recurse is True, also yields articles of the subcategories.
        Recurse can be a number to restrict the depth at which subcategories
        are included.

        Results a sorted (as sorted by MediaWiki), but need not be unique.
        """
        for type, title in self._getContentsAndSupercats(recurse = recurse, startFrom = startFrom):
            if type == ARTICLE:
                yield wikipedia.Page(self.site(), title)

    def articlesList(self, recurse = False):
        """
        Creates a list of all articles of the current category.

        If recurse is True, also return articles of the subcategories.
        Recurse can be a number to restrict the depth at which subcategories
        are included.

        The elements of the returned list are sorted (as sorted by MediaWiki)
        and unique.
        """
        articles = []
        for article in self.articles(recurse = recurse):
            articles.append(article)
        return unique(articles)

    def supercategories(self):
        """
        Yields all supercategories of the current category.

        Results a sorted in the order in which they were entered, and need not
        be unique.
        """
        for type, title in self._getContentsAndSupercats():
            if type == SUPERCATEGORY:
                yield Category(self.site(), title)

    def supercategoriesList(self):
        """
        Creates a list of all supercategories of the current category.

        The elements of the returned list are unique and appear in the order
        in which they were entered.
        """
        supercats = []
        for cat in self.supercategories():
            supercats.append(cat)
        return unique(supercats)

    def isEmpty(self):
        # TODO: rename; naming conflict with Page.isEmpty
        for type, title in self._getContentsAndSupercats():
            if type == ARTICLE or type == SUBCATEGORY:
                return False
        return True

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

    #Like copyTo above, except this removes a list of templates (like deletion templates) that appear in
    #the old category text.  It also removes all text between the two HTML comments BEGIN CFD TEMPLATE
    #and END CFD TEMPLATE. (This is to deal with CFD templates that are substituted.)
    def copyAndKeep(self, catname, cfdTemplates):
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
	    newtext = self.get()
	    for regexName in cfdTemplates:
	        matchcfd = re.compile(r"{{%s.*?}}" % regexName, re.IGNORECASE)
	        newtext = matchcfd.sub('',newtext)
            matchcomment = re.compile(r"<!--BEGIN CFD TEMPLATE-->.*<!--END CFD TEMPLATE-->", re.IGNORECASE | re.MULTILINE | re.DOTALL)
            newtext = matchcomment.sub('',newtext)
            pos = 0
            while (newtext[pos:pos+1] == "\n"):
                pos = pos + 1
            newtext = newtext[pos:]
	    targetCat.put(newtext, creationSummary)
            return True
    
#def Category(code, name):
#    """Factory method to create category link objects from the category name"""
#    # Standardized namespace
#    ns = wikipedia.getSite().category_namespaces()[0]
#    # Prepend it
#    return Category(code, "%s:%s" % (ns, name))

def change_category(article, oldCat, newCat, comment=None, sortKey=None, inPlace=False):
    """
    Given an article which is in category oldCat, moves it to
    category newCat. Moves subcategories of oldCat as well.
    oldCat and newCat should be Category objects.
    If newCat is None, the category will be removed.
    """
    cats = article.categories(nofollow_redirects=True)
    site = article.site()
    changesMade = False

    if inPlace == True:
        text = article.get(nofollow_redirects=True)
        text = wikipedia.replaceCategoryInPlace(text, oldCat, newCat)
        try:
            article.put(text, comment)
        except wikipedia.EditConflict:
            wikipedia.output(u'Skipping %s because of edit conflict' % (article.title()))
        return

    # This loop will replace all occurrences of the category to be changed, and remove duplicates.
    newCatList = []
    newCatSet = set()
    for i in range(len(cats)):
        cat = cats[i]
        if cat == oldCat:
            changesMade = True
            if not sortKey:
                sortKey = cat.sortKey
            if newCat:
                if newCat.title() not in newCatSet:
                    newCategory = Category(site, newCat.title(), sortKey = sortKey)
                    newCatSet.add(newCat.title())
                    newCatList.append(newCategory)
        elif cat.title() not in newCatSet:
            newCatSet.add(cat.title())
            newCatList.append(cat)

    if not changesMade:
        wikipedia.output(u'ERROR: %s is not in category %s!' % (article.aslink(), oldCat.title()))
    else:
        text = article.get(nofollow_redirects=True)
        try:
            text = wikipedia.replaceCategoryLinks(text, newCatList)
        except ValueError:   #Make sure that the only way replaceCategoryLinks() can return a ValueError is in the case of interwiki links to self.
            wikipedia.output(u'Skipping %s because of interwiki link to self' % (article))
        try:
            article.put(text, comment)
        except wikipedia.EditConflict:
            wikipedia.output(u'Skipping %s because of edit conflict' % (article.title()))
        except wikipedia.SpamfilterError:
            wikipedia.output(u'Skipping %s because of spam filter error' % (article.title()))

def test():
    site = wikipedia.getSite()
    
    cat = Category(site, 'Category:Software')
    
    wikipedia.output(u'SUBCATEGORIES:')
    for subcat in cat.subcategories():
        wikipedia.output(subcat.title())
    wikipedia.output(u'\nARTICLES:')
    for article in cat.articles():
        wikipedia.output(article.title())

if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        wikipedia.output(u'Ignored argument: %s' % arg)
    test()
