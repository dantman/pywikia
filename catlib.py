#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Library to work with category pages on Wikipedia
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2004-2007
# (C) Daniel Herding, 2004-2007
# (C) Russell Blau, 2005
# (C) Cyde Weys, 2005-2007
# (C) Leonardo Gregianin, 2005-2007
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
    'id':u'Bot: Memindahkan dari %s. Kontributor: %s',
    'it':u'Bot: Voce spostata da %s. Autori: %s',
    'fr':u'Robot : déplacé depuis %s. Auteurs: %s',
    'he':u'בוט: הועבר מהשם %s. כותבים: %s',
    'nl':u'Bot: hernoemd van %s. Auteurs: %s',
    'pl':u'Robot przenosi z %s. Autorzy: %s',
    'pt':u'Bot: Movido de %s. Autor: %s',
    'zh':u'機器人: 已從 %s 移動。原作者是 %s',
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

    def _getContentsAndSupercats(self, recurse=False, purge=False,
                                 startFrom=None, cache=None):
        """
        Cache results of _parseCategory for a second call.

        If recurse is a bool, and value is True, then recursively retrieves
        contents of all subcategories without limit. If recurse is an int,
        recursively retrieves contents of subcategories to that depth only.

        Other parameters are analogous to _parseCategory(). If purge is True,
        cached results will be discarded. If startFrom is used, nothing
        will be cached.

        This should not be used outside of this module.
        """
        if cache is None:
            cache = []
        if purge:
            self.completelyCached = False
        if recurse:
            if type(recurse) is int:
                newrecurse = recurse - 1
            else:
                newrecurse = recurse
        if self.completelyCached:
            for article in self.articleCache:
                if article not in cache:
                    cache.append(article)
                    yield ARTICLE, article
            for subcat in self.subcatCache:
                if subcat not in cache:
                    cache.append(subcat)
                    yield SUBCATEGORY, subcat
                    if recurse:
                        # contents of subcategory are cached by calling
                        # this method recursively; therefore, do not cache
                        # them again
                        for item in subcat._getContentsAndSupercats(newrecurse,
                                                           purge, cache=cache):
                            if item[0] != SUPERCATEGORY:
                                yield item
            for supercat in self.supercatCache:
                yield SUPERCATEGORY, supercat
        else:
            for tag, page in self._parseCategory(purge, startFrom):
                if tag == ARTICLE:
                    self.articleCache.append(page)
                    if not page in cache:
                        cache.append(page)
                        yield ARTICLE, page
                elif tag == SUBCATEGORY:
                    self.subcatCache.append(page)
                    if not page in cache:
                        cache.append(page)
                        yield SUBCATEGORY, page
                        if recurse:
                            # contents of subcategory are cached by calling
                            # this method recursively; therefore, do not cache
                            # them again
                            for item in page._getContentsAndSupercats(
                                             newrecurse, purge, cache=cache):
                                if item[0] != SUPERCATEGORY:
                                    yield item
                elif tag == SUPERCATEGORY:
                    self.supercatCache.append(page)
                    yield SUPERCATEGORY, page
            if not startFrom:
                self.completelyCached = True

    def _parseCategory(self, purge=False, startFrom=None):
        """
        Yields all articles and subcategories that are in this category,
        as well as its supercategories.

        Set purge to True to instruct MediaWiki not to serve a cached version.

        Set startFrom to a string which is the title of the page to start from.

        Yielded results are tuples in the form (tag, page) where tag is one
        of the constants ARTICLE, SUBCATEGORY and SUPERCATEGORY, and title is
        the Page or Category object.

        Note that results of this method need not be unique.

        This should not be used outside of this module.
        """
        if self.site().versionnumber() < 4:
            Rtitle = re.compile('title\s?=\s?\"([^\"]*)\"')
        elif self.site().versionnumber() < 8:
            Rtitle = re.compile('/\S*(?: title\s?=\s?)?\"([^\"]*)\"')
        else:
            Rtitle = re.compile(
            '<li>(?:<span.*?>)?<a href=\".*?\"\s?title\s?=\s?\"([^\"]*)\"\>\+?[^\<\+]')
        if self.site().versionnumber() < 8:
            Rsubcat = None
            Rimage = None
        else:
            Rsubcat = re.compile(
                'CategoryTreeLabelCategory\"\s?href=\".+?\">(.+?)</a>')
            Rimage = re.compile(
                '<div class\s?=\s?\"thumb\"\sstyle=\"[^\"]*\">(?:<div style=\"[^\"]*\">)?<a href=\".*?\"(?:\sclass="image")?\stitle\s?=\s?\"([^\"]*)\"')
        ns = self.site().category_namespaces()
        # regular expression matching the "(next 200)" link
        RLinkToNextPage = re.compile('&amp;from=(.*?)" title="');

        currentPageOffset = startFrom
        while True:
            path = self.site().get_address(self.urlname())
            if purge:
                path += '&action=purge'
            if currentPageOffset:
                path += '&from=' + currentPageOffset
                wikipedia.output('Getting [[%s]] starting at %s...'
                                 % (self.title(), currentPageOffset))
            else:
                wikipedia.output('Getting [[%s]]...' % self.title())
            wikipedia.get_throttle()
            txt = self.site().getUrl(path)
            # save a copy of this text to find out self's supercategory.
            self_txt = txt
            # index where subcategory listing begins
            try:
                ibegin = txt.index('<div id="mw-subcategories">')
                skippedCategoryDescription = True
            except ValueError:
                try:
                    ibegin = txt.index('<div id="mw-pages">')
                    skippedCategoryDescription = True
                except ValueError:
                    try:
                        ibegin = txt.index('<!-- start content -->') # does not work for cats without text
                        skippedCategoryDescription = False
                    except ValueError:
                        wikipedia.output("\nCategory page detection is not bug free. Please report this error!")
                        raise
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
                    yield SUBCATEGORY, ncat
                else:
                    yield ARTICLE, wikipedia.Page(self.site(), title)
            if Rsubcat:
                # For MediaWiki versions where subcats look differently
                for titleWithoutNamespace in Rsubcat.findall(txt):
                    title = 'Category:%s' % titleWithoutNamespace
                    ncat = Category(self.site(), title)
                    yield SUBCATEGORY, ncat
            if Rimage:
                # For MediaWiki versions where images work through galleries
                for title in Rimage.findall(txt):
                    # In some MediaWiki versions, the titles contain the namespace,
                    # but they don't in other (newer) versions. Use the ImagePage's
                    # defaultNamespace feature to get everything correctly.
                    yield ARTICLE, wikipedia.ImagePage(self.site(), title)
            # try to find a link to the next list page
            # If skippedCategoryDescription is False, then there are no pages
            # or subcategories, so there cannot be a next list page
            if skippedCategoryDescription:
                matchObj = RLinkToNextPage.search(txt)
                if matchObj:
                    currentPageOffset = matchObj.group(1)
                    wikipedia.output('There are more articles in %s.'
                                     % self.title())
                else:
                    break
            else:
                break
            
        # get supercategories
        try:
            ibegin = self_txt.index('<div id="catlinks">')
            iend = self_txt.index('<!-- end content -->')
        except ValueError:
            # no supercategories found
            pass
        else:
            self_txt = self_txt[ibegin:iend]
            if self.site().versionnumber() < 5:
                # MediaWiki 1.4 has an unneeded space here
                Rsupercat = re.compile('title ="([^"]*)"')
            else:
                Rsupercat = re.compile('title="([^"]*)"')
            for title in Rsupercat.findall(self_txt):
                # There might be a link to Special:Categories we don't want
                if isCatTitle(title, self.site()):
                    yield SUPERCATEGORY, title

    def subcategories(self, recurse=False):
        """
        Yields all subcategories of the current category.

        If recurse is True, also yields subcategories of the subcategories.
        If recurse is a number, also yields subcategories of subcategories,
        but only at most that number of levels deep (that is, recurse = 0 is
        equivalent to recurse = False, recurse = 1 gives first-level
        subcategories of subcategories but no deeper, etcetera).

        Results a sorted (as sorted by MediaWiki), but need not be unique.
        """
        for tag, subcat in self._getContentsAndSupercats(recurse):
            if tag == SUBCATEGORY:
                yield subcat

    def subcategoriesList(self, recurse=False):
        """
        Creates a list of all subcategories of the current category.

        If recurse is True, also return subcategories of the subcategories.
        Recurse can also be a number, as explained above.

        The elements of the returned list are sorted and unique.
        """
        subcats = []
        for cat in self.subcategories(recurse):
            subcats.append(cat)
        return unique(subcats)

    def articles(self, recurse=False, startFrom=None):
        """
        Yields all articles of the current category.

        If recurse is True, also yields articles of the subcategories.
        Recurse can be a number to restrict the depth at which subcategories
        are included.

        Results are unsorted (except as sorted by MediaWiki), and need not
        be unique.
        """
        for tag, page in self._getContentsAndSupercats(recurse, startFrom=startFrom):
            if tag == ARTICLE:
                yield page

    def articlesList(self, recurse=False):
        """
        Creates a list of all articles of the current category.

        If recurse is True, also return articles of the subcategories.
        Recurse can be a number to restrict the depth at which subcategories
        are included.

        The elements of the returned list are sorted and unique.
        """
        articles = []
        for article in self.articles(recurse):
            articles.append(article)
        return unique(articles)

    def supercategories(self):
        """
        Yields all supercategories of the current category.

        Results are stored in the order in which they were entered, and need
        not be unique.
        """
        for tag, supercat in self._getContentsAndSupercats():
            if tag == SUPERCATEGORY:
                yield supercat

    def supercategoriesList(self):
        """
        Creates a list of all supercategories of the current category.

        The elements of the returned list are sorted and unique.
        """
        supercats = []
        for cat in self.supercategories():
            supercats.append(cat)
        return unique(supercats)

    def isEmpty(self):
        # TODO: rename; naming conflict with Page.isEmpty
        for tag, title in self._getContentsAndSupercats(purge = True):
            if tag in (ARTICLE, SUBCATEGORY):
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
        oldtext = article.get(nofollow_redirects=True)
        newtext = wikipedia.replaceCategoryInPlace(oldtext, oldCat, newCat)
        if newtext == oldtext:
            wikipedia.output(
                u'No changes in made in page %s.' % article.aslink())
            return
        try:
            article.put(newtext, comment)
        except wikipedia.EditConflict:
            wikipedia.output(
                u'Skipping %s because of edit conflict' % article.aslink())
        except wikipedia.LockedPage:
            wikipedia.output(u'Skipping locked page %s' % article.aslink())
        except wikipedia.SpamfilterError, error:
            wikipedia.output(
                u'Changing page %s blocked by spam filter (URL=%s)'
                             % (article.aslink(), error.url))
        except wikipedia.NoUsername:
            wikipedia.output(
                u"Page %s not saved; sysop privileges required."
                             % article.aslink())
        except wikipedia.PageNotSaved, error:
            wikipedia.output(u"Saving page %s failed: %s"
                             % (article.aslink(), error.message))
        return

    # This loop will replace all occurrences of the category to be changed,
    # and remove duplicates.
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
                    newCategory = Category(site, newCat.title(),
                                           sortKey=sortKey)
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
        except ValueError:
            # Make sure that the only way replaceCategoryLinks() can return
            # a ValueError is in the case of interwiki links to self.
            wikipedia.output(
                    u'Skipping %s because of interwiki link to self' % article)
        try:
            article.put(text, comment)
        except wikipedia.EditConflict:
            wikipedia.output(
                    u'Skipping %s because of edit conflict' % article.title())
        except wikipedia.SpamfilterError, e:
            wikipedia.output(
                    u'Skipping %s because of blacklist entry %s'
                    % (article.title(), e.url))
        except wikipedia.LockedPage:
            wikipedia.output(
                    u'Skipping %s because page is locked' % article.title())

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
