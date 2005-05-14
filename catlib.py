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
import re, time
import wikipedia

msg_created_for_renaming = {
    'de':u'Bot: Verschoben von %s. Autoren: %s',
    'en':u'Robot: Moved from %s. Authors: %s',
    'fr':u'Robot : déplacé depuis %s. Auteurs: %s',
    }

class CatTitleRecognition(object):
    """Special object to recognize categories in a certain language.

       Purpose is to construct an object using a language code, and
       to call the object as a function to see whether a title represents
       a category page.
    """
    def __init__(self, site):
        self.ns = site.category_namespaces()

    def check(self, s):
        """True if s points to a category page."""
        # try different possibilities for namespaces
        # (first letter lowercase, English 'category')
        for ins in self.ns:
            if s.startswith(ins + ':'):
                return True
        return False
        
def unique(l):
    """Given a list of hashable object, return an alphabetized unique list.
    """
    l=dict.fromkeys(l).keys()
    l.sort()
    return l
    
class _CatLink(wikipedia.Page):
    """Subclass of Page that has some special tricks that only work for
       category: pages"""

    def iscattitle(self, title):
        return CatTitleRecognition(wikipedia.getSite()).check(title)
        
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
            site = wikipedia.getSite()
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
                target = cat.urlname()
                if startFromPage:
                    target += '&from=' + startFromPage
                if purge:
                    target += '&action=purge'
                # this loop will run until the page could be retrieved
                # Try to retrieve the page until it was successfully loaded (just in case
                # the server is down or overloaded)
                # wait for retry_idle_time minutes (growing!) between retries.
                retry_idle_time = 1
                while True:
                    try:
                        txt = wikipedia.getPage(site, target, get_edit_page = False)
                    except:
                        # We assume that the server is down. Wait some time, then try again.
                        raise
                        print "WARNING: There was a problem retrieving %s. Maybe the server is down. Retrying in %d minutes..." % (cat.linkname(), retry_idle_time)
                        time.sleep(retry_idle_time * 60)
                        # Next time wait longer, but not longer than half an hour
                        retry_idle_time *= 2
                        if retry_idle_time > 30:
                            retry_idle_time = 30
                        continue
                    break
                
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
                    if self.iscattitle(title):
                        ncat = _CatLink(self.site(), title)
                        if recurse and ncat not in catsdone:
                            catstodo.append(ncat)
                        subcats.append(title)
                    else:
                        articles.append(title)
                # try to find a link to the next list page
                matchObj = RLinkToNextPage.search(txt)
                if matchObj:
                    startFromPage = matchObj.group(1)
                    wikipedia.output('There are more articles in %s.' % cat.linkname())
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
            Rsupercat = re.compile('title ="([^"]*)"')
            for title in Rsupercat.findall(self_txt):
                # There might be a link to Special:Categories we don't want
                if self.iscattitle(title):
                    supercats.append(title)
        return (articles, subcats, supercats)
    
    def subcategories(self, recurse = False):
        """Create a list of all subcategories of the current category.

           If recurse = True, also return subcategories of the subcategories.

           Returns a sorted, unique list of all subcategories.
        """
        subcats = []
        for title in self.catlist(recurse)[1]:
            ncat = _CatLink(self.site(), title)
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
            ncat = _CatLink(self.site(), title)
            supercats.append(ncat)
        return unique(supercats)
    
    def isEmpty(self):
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
            wikipedia.output('Target page %s already exists!' % targetCat.linkname())
            return False
        else:
            wikipedia.output('Moving text from %s to %s.' % (self.linkname(), targetCat.linkname()))
            authors = ', '.join(self.contributingUsers())
            creationSummary = wikipedia.translate(wikipedia.getSite(), msg_created_for_renaming) % (self.linkname(), authors)
            targetCat.put(self.get(), creationSummary)
            return True
    
def CatLink(code, name):
    """Factory method to create category link objects from the category name"""
    # Standardized namespace
    ns = wikipedia.getSite().category_namespaces()[0]
    # Prepend it
    return _CatLink(code, "%s:%s" % (ns, name))

# Given an article which is in category old_cat, moves it to
# category new_cat. Moves subcategories of old_cat to new_cat
# as well.
# If new_cat_title is None, the category will be removed.
def change_category(article, old_cat_title, new_cat_title):
    print ''
    cats = article.rawcategories()
    site = article.site()
    sort_key = ''
    removed = False
    for cat in cats:
        cattext = cat.linkname().split('|')[0].split(':', 1)[1]
        if cattext == old_cat_title:
            # because a list element is removed, the iteration will skip the 
            # next element. this might lead to forgotten categories, but
            # usually each category should only appear once per article.
            cats.remove(cat)
            removed = True
        elif cattext.startswith(old_cat_title + '|'):
            sort_key = cat.catname().split('|', 1)[1]
            cats.remove(cat)
            removed = True
    if not removed:
        wikipedia.output(u'ERROR: %s is not in category %s!' % (article.aslink(), old_cat_title))
        return
    if new_cat_title != None:
        if sort_key == '':
            new_cat = CatLink(site, new_cat_title)
        else:
            new_cat = CatLink(site, new_cat_title + '|' + sort_key)
        cats.append(new_cat)
    text = article.get()
    text = wikipedia.replaceCategoryLinks(text, cats)
    article.put(text)


def test():
    site = wikipedia.getSite()
    
    pl=CatLink(site, 'Software')
    
    print pl.catlist(recurse = False)

    print pl.subcategories(recurse = False)

    print pl.articles(recurse = False)

if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            print "Ignored argument", arg
    test()
