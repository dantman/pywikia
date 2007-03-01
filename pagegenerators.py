#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This module offers a wide variety of page generators. A page generator is an
object that is iterable (see http://www.python.org/dev/peps/pep-0255/ ) and
that yields page objects on which other scripts can then work.

In general, there is no need to run this script directly. It can, however,
be run for testing purposes.
"""
__version__='$Id$'

# Standard library imports
import re, codecs, sys
import urllib, time

# Application specific imports
import wikipedia, date, catlib
import config

def AllpagesPageGenerator(start ='!', namespace = None):
    """
    Using the Allpages special page, retrieve all articles' titles, and yield
    page objects.
    """
    if namespace==None:
        namespace = wikipedia.Page(wikipedia.getSite(), start).namespace()
    for page in wikipedia.getSite().allpages(start=start, namespace=namespace):
        yield page
    
def PrefixingPageGenerator(prefix, namespace=None):
    for page in AllpagesPageGenerator(prefix, namespace):
        if page.titleWithoutNamespace().startswith(prefix):
            yield page
        else:
            break

def NewpagesPageGenerator(number = 100, repeat = False, site = None):
    if site is None:
        site = wikipedia.getSite()
    for page in site.newpages(number=number, repeat=repeat):
        yield page[0]
        
def FileLinksGenerator(referredPage):
    for page in referredPage.getFileLinks():
        yield page

def ImagesPageGenerator(pageWithImages):
    for page in pageWithImages.imagelinks(followRedirects = False, loose = True):
        yield page

def ReferringPageGenerator(referredPage, followRedirects=False,
                           withTemplateInclusion=True,
                           onlyTemplateInclusion=False):
    '''Yields all pages referring to a specific page.'''
    for page in referredPage.getReferences(followRedirects,
                                           withTemplateInclusion,
                                           onlyTemplateInclusion):
        yield page

def ReferringPagesGenerator(referredPages, followRedirects=False,
                            withTemplateInclusion=True,
                            onlyTemplateInclusion=False):
    """Yields all unique pages referring to a list of specific pages."""
    allPages = []
    for referredPage in referredPages:
        for page in referredPage.getReferences(followRedirects,
                                               withTemplateInclusion,
                                               onlyTemplateInclusion):
            allPages.append(page)

    #Remove duplicate pages.
    allPages = list(set(allPages))
    wikipedia.output(u'Page generator found %s pages.' % len(allPages))

    for page in allPages:
        yield page

def CategorizedPageGenerator(category, recurse = False, start='!'):
    '''
    Yields all pages in a specific category.
    If recurse is True, pages in subcategories are included as well.
    If start has a value, only pages whose title comes after start
    alphabetically are included.
    '''
    for page in category.articles(recurse=recurse):
        if page.title() >= start:
            yield page

def CategoryPartPageGenerator(category, start = None):
    '''
    Yields 200 pages in a category; for categories with 1000s of articles
    CategorizedPageGenerator is too slow.
    '''
    # The code is based on _make_catlist in catlib.py; probably the two should
    # be merged, with this generator being moved to catlib.py and _make_catlist
    # using it.
    site = wikipedia.getSite()
    if site.version() < "1.4":
        Rtitle = re.compile('title\s?=\s?\"([^\"]*)\"')
    else:
        Rtitle = re.compile('<li><a href="/.*?" title=".*?">([^]<>].*?)</a></li>')
    RLinkToNextPage = re.compile('&amp;from=(.*?)" title="');
    while True:
        path = site.get_address(category.urlname())
        if start:
            path = path + '&from=%s' % wikipedia.Page(site, start).urlname()
            wikipedia.output(u'Getting [[%s]] starting at %s...'
                               % (category.title(), start))
        else:
            wikipedia.output(u'Getting [[%s]...' % category.title())
        txt = site.getUrl(path)
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
            page = wikipedia.Page(site, title)
            if page.namespace() != 14:
                yield page
        matchObj = RLinkToNextPage.search(txt)
        if matchObj:
            start = matchObj.group(1)
        else:
            break

def LinkedPageGenerator(linkingPage):
    """Yields all pages linked from a specific page."""
    for page in linkingPage.linkedPages():
        yield page

def TextfilePageGenerator(filename=None):
    '''
    Read a file of page links between double-square-brackets, and return
    them as a list of Page objects. filename is the name of the file that
    should be read. If no name is given, the generator prompts the user.
    '''
    if filename is None:
        filename = wikipedia.input(u'Please enter the filename:')
    site = wikipedia.getSite()
    f = codecs.open(filename, 'r', config.textfile_encoding)
    R = re.compile(ur'\[\[(.+?)(?:\]\]|\|)') # title ends either before | or before ]]
    for pageTitle in R.findall(f.read()):
        site = wikipedia.getSite()
        # If the link doesn't refer to this site, the Page constructor
        # will automatically choose the correct site.
        # This makes it possible to work on different wikis using a single
        # text file, but also could be dangerous because you might
        # inadvertently change pages on another wiki!
        yield wikipedia.Page(site, pageTitle)
    f.close()

def PagesFromTitlesGenerator(iterable):
    """Generates pages from the titles (unicode strings) yielded by iterable"""
    for title in iterable:
        if not isinstance(title, basestring):
            break
        yield wikipedia.Page(wikipedia.getSite(), title)


class GoogleSearchPageGenerator:
    '''
    To use this generator, you must install the pyGoogle module from
    http://pygoogle.sf.net/ and get a Google Web API license key from
    http://www.google.com/apis/index.html . The google_key must be set to your
    license key in your configuration.
    '''
    def __init__(self, query = None):
        self.query = query or wikipedia.input(u'Please enter the search query:')
    
    def queryGoogle(self, query):
        import google
        google.LICENSE_KEY = config.google_key
        offset = 0
        estimatedTotalResultsCount = None
        while not estimatedTotalResultsCount or offset < estimatedTotalResultsCount:
            while (True):
                # Google often yields 502 errors. 
                try:
                    wikipedia.output(u'Querying Google, offset %i' % offset)
                    data = google.doGoogleSearch(query, start = offset, filter = False)
                    break
                except:
                    # SOAPpy.Errors.HTTPError or SOAP.HTTPError (502 Bad Gateway)
                    # can happen here, depending on the module used. It's not easy
                    # to catch this properly because pygoogle decides which one of
                    # the soap modules to use.
                    wikipedia.output(u"An error occured. Retrying in 10 seconds...")
                    time.sleep(10)
                    continue

            for result in data.results:
                #print 'DBG: ', result.URL
                yield result.URL
            # give an estimate of pages to work on, but only once.
            if not estimatedTotalResultsCount:
                wikipedia.output(u'Estimated total result count: %i pages.' % data.meta.estimatedTotalResultsCount)
            estimatedTotalResultsCount = data.meta.estimatedTotalResultsCount
            #print 'estimatedTotalResultsCount: ', estimatedTotalResultsCount
            offset += 10
        
    def __iter__(self):
        site = wikipedia.getSite()
        # restrict query to local site
        localQuery = '%s site:%s' % (self.query, site.hostname())
        base = 'http://%s%s' % (site.hostname(), site.nice_get_address(''))
        for url in self.queryGoogle(localQuery):
            if url[:len(base)] == base:
                title = url[len(base):]
                page = wikipedia.Page(site, title)
                yield page

def MySQLPageGenerator(query):
    '''

    '''
    import MySQLdb as mysqldb
    site = wikipedia.getSite()
    conn = mysqldb.connect(config.db_hostname, db = site.dbName(),
                           user = config.db_username,
                           passwd = config.db_password)
    cursor = conn.cursor()
    wikipedia.output(u'Executing query:\n%s' % query)
    query = query.encode(site.encoding())
    cursor.execute(query)
    while True:
        try:
            namespaceNumber, pageName = cursor.fetchone()
            print namespaceNumber, pageName
        except TypeError:
            # Limit reached or no more results
            break
        #print pageName
        if pageName:
            namespace = site.namespace(namespaceNumber)
            pageName = unicode(pageName, site.encoding())
            if namespace:
                pageTitle = '%s:%s' % (namespace, pageName)
            else:
                pageTitle = pageName
            page = wikipedia.Page(site, pageTitle)
            yield page

def YearPageGenerator(start = 1, end = 2050):
    wikipedia.output(u"Starting with year %i" % start)
    for i in xrange(start, end + 1):
        if i % 100 == 0:
            wikipedia.output(u'Preparing %i...' % i)
        # There is no year 0
        if i != 0:
            current_year = date.formatYear(wikipedia.getSite().lang, i )
            yield wikipedia.Page(wikipedia.getSite(), current_year)

def DayPageGenerator(startMonth=1, endMonth=12):
    fd = date.FormatDate(wikipedia.getSite())
    firstPage = wikipedia.Page(wikipedia.getSite(), fd(startMonth, 1))
    wikipedia.output(u"Starting with %s" % firstPage.aslink())
    for month in xrange(startMonth, endMonth+1):
        for day in xrange(1, date.getNumberOfDaysInMonth(month)+1):
            yield wikipedia.Page(wikipedia.getSite(), fd(month, day))

def NamespaceFilterPageGenerator(generator, namespaces):
    """
    Wraps around another generator. Yields only those pages that are in a list
    of specific namespace.
    """
    for page in generator:
        if page.namespace() in namespaces:
            yield page

def RedirectFilterPageGenerator(generator):
    """
    Wraps around another generator. Yields only those pages that are not redirects.
    """
    for page in generator:
        if not page.isRedirectPage():
            yield page

def CombinedPageGenerator(generators):
    """
    Wraps around a list of other generators. Yields all pages generated by the
    first generator; when the first generator stops yielding pages, yields those
    generated by the second generator, etc.
    """
    for generator in generators:
        for page in generator:
            yield page

def CategoryGenerator(generator):
    """
    Wraps around another generator. Yields the same pages, but as Category
    objects instead of Page objects. Makes sense only if it is ascertained
    that only categories are being retrieved.
    """
    for page in generator:
        yield catlib.Category(page.site(), page.title())

def PageWithTalkPageGenerator(generator):
    """
    Wraps around another generator. Yields the same pages, but for non-talk pages, it
    also includes associated talk pages.
    This generator does not check if the talk page in fact exists.
    """
    for page in generator:
        yield page
        if not page.isTalkPage():
            yield page.toggleTalkPage()

def PreloadingGenerator(generator, pageNumber=60):
    """
    Wraps around another generator. Retrieves as many pages as stated by pageNumber
    from that generator, loads them using Special:Export, and yields them one after
    the other. Then retrieves more pages, etc.
    """

    def preload(pages):
        try:
            site = pages[0].site()
            wikipedia.getall(site, pages, throttle=False)
        except IndexError:
            # Can happen if the pages list is empty. Don't care.
            pass
        except wikipedia.SaxError:
            # Ignore this error, and get the pages the traditional way later.
            pass

    # this array will contain up to pageNumber pages and will be flushed
    # after these pages have been preloaded and yielded.
    somePages = []
    for page in generator:
        somePages.append(page)
        # We don't want to load too many pages at once using XML export.
        # We only get a maximum number at a time.
        if len(somePages) >= pageNumber:
            preload(somePages)
            for refpage in somePages:
                yield refpage
            somePages = []
    if somePages:
        # preload remaining pages
        preload(somePages)
        for refpage in somePages:
            yield refpage

class GeneratorFactory:
    """
    This factory is responsible for processing command line arguments
    that are used many scripts and that determine on which pages
    to work on.
    """
    def __init__(self):
        pass

    def handleArg(self, arg):
        if arg.startswith('-filelinks'):
            if len(arg) == 10:
                fileLinksPageTitle = wikipedia.input(u'Links to which image page should be processed?')
            else:
                fileLinksPageTitle = arg[11:]
            fileLinksPage = wikipedia.Page(wikipedia.getSite(), 'Image:' + fileLinksPageTitle)
            return FileLinksGenerator(fileLinksPage)
        elif arg.startswith('-file'):
            if len(arg) >= 6:
                textfilename = arg[6:]
            return TextfilePageGenerator(textfilename)
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                categoryname = wikipedia.input(u'Please enter the category name:')
            else:
                categoryname = arg[5:]
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryname)
            return CategorizedPageGenerator(cat)
        elif arg.startswith('-subcat'):
            if len(arg) == 7:
                categoryname = wikipedia.input(u'Please enter the category name:')
            else:
                categoryname = arg[8:]
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryname)
            return CategorizedPageGenerator(cat, recurse = True)
        elif arg.startswith('-ref'):
            if len(arg) == 4:
                referredPageTitle = wikipedia.input(u'Links to which page should be processed?')
            else:
                referredPageTitle = arg[5:]
            referredPage = wikipedia.Page(wikipedia.getSite(), referredPageTitle)
            return ReferringPageGenerator(referredPage)
        elif arg.startswith('-links'):
            if len(arg) == 6:
                linkingPageTitle = wikipedia.input(u'Links from which page should be processed?')
            else:
                linkingPageTitle = arg[7:]
            linkingPage = wikipedia.Page(wikipedia.getSite(), linkingPageTitle)
            return LinkedPageGenerator(linkingPage)
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = wikipedia.input(u'At which page do you want to start?')
            else:
                firstPageTitle = arg[7:]
            namespace = wikipedia.Page(wikipedia.getSite(), firstPageTitle).namespace()
            firstPageTitle = wikipedia.Page(wikipedia.getSite(), firstPageTitle).titleWithoutNamespace()
            return AllpagesPageGenerator(firstPageTitle, namespace)
        elif arg.startswith('-new'):
            if len(arg) >=5:
              return NewpagesPageGenerator(number = int(arg[5:]))
            else:
              return NewpagesPageGenerator(number = 60)
        elif arg.startswith('-google'):
            if len(arg) == 8:
                googleQuery = wikipedia.input(u'What do you want to search for?')
            else:
                googleQuery = arg[8:]
            return GoogleSearchPageGenerator(googleQuery)
        else:
            return None

# This class was written before GeneratorFactory. It was intended for the same
# purpose, but it is not used anywhere.
class CommandLineGenerator(object):
    """Make a generator by parsing command line arguments."""
    def __init__(self):
        self.genclass = None
        self.start = None

    def setClass(self, newclass, **kw):
        if self.genclass != None:
            print "ERROR: More than one page generator specified on command line"
            sys.exit(1)
        self.genclass = (newclass, kw)
        self.start = None

    def handleArgs(self, args):
        unhandledArgs = []
        for arg in args:
            if arg == '-newpages':
                self.setClass(NewpagesPageGenerator)
            elif arg == '-allpages':
                self.setClass(AllpagesPageGenerator)
            elif arg.startswith('-start:'):
                self.start = arg[7:]
            elif arg.startswith('-pageprefix:'):
                self.setClass(PrefixingPageGenerator, prefix=arg[12:])
            elif arg.startswith('-filelinks:'):
                page = wikipedia.Page(None, arg[11:])
                self.setClass(FileLinksGenerator, referredPage=page)
            elif arg.startswith('-incat:'):
                cat = catlib.Category(None, arg[7:])
                self.setClass(CategorizedPageGenerator, cat=cat, recurse=False)
            elif arg.startswith('-insubcat:'):
                cat = catlib.Category(None, arg[10:])
                self.setClass(CategorizedPageGenerator, cat=cat, recurse=True)
            elif arg.startswith('-referringto:'):
                page = wikipedia.Page(None, arg[13:])
                self.setClass(ReferringPageGenerator, referredPage=page)
            elif arg.startswith('-google:'):
                self.setClass(GoogleSearchPageGenerator, query = arg[8:])
            else:
                unhandledArgs.append(arg)
        return unhandledArgs

    def get(self):
        """Generate an instance of the class"""
        if self.genclass:
            cl = self.genclass[0]
            kw = self.genclass[1]
        else:
            cl = None
            kw = {}
        # Add the start argument to the keyword arguments
        if self.start:
            kw['start'] = self.start
            # The start argument can be used without an explicit
            # class. In that case use the allpages generator.
            if cl is None:
                cl = AllpagesPageGenerator
        if cl:
            return cl(**kw)
        else:
            return None

if __name__ == "__main__":
    try:
        genFactory = GeneratorFactory()
        for arg in wikipedia.handleArgs():
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
        for page in gen:
            wikipedia.output(page.title(), toStdout = True)
        # This test code did not work. --Daniel
        #clg = CommandLineGenerator()
        #args = wikipedia.handleArgs()
        #args = clg.handleArgs(args)
        #for arg in args:
            #wikipedia.output("WARNING: Unhandled argument %s" % arg)
        #g = clg.get()
        #i = 0
        #for p in g:
            #i += 1
            #if i > 100:
                #break
            #print p
    finally:
        wikipedia.stopme()

