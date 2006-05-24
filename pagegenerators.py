#!/usr/bin/python
# -*- coding: utf-8  -*-

__version__='$Id$'

# Standard library imports
import re, codecs, sys

# Application specific imports
import wikipedia, date
import config

class AllpagesPageGenerator:
    '''
    Using the Allpages special page, retrieves all articles, loads them (60 at
    a time) using XML export, and yields title/text pairs.
    '''
    def __init__(self, start ='!', namespace = None):
        self.start = start
        if namespace==None:
            self.namespace = wikipedia.Page(wikipedia.getSite(),start).namespace()
        else:
            self.namespace = namespace

    def __iter__(self):
        for page in wikipedia.getSite().allpages(start = self.start, namespace = self.namespace):
            yield page

class ReferringPageGenerator:
    '''
    Yields all pages referring to a specific page.
    '''
    def __init__(self, referredPage, followRedirects = False, withTemplateInclusion = True, onlyTemplateInclusion = False):
        self.referredPage = referredPage
        self.followRedirects = followRedirects
        self.withTemplateInclusion = withTemplateInclusion
        self.onlyTemplateInclusion = onlyTemplateInclusion

    def __iter__(self):
        for page in self.referredPage.getReferences(follow_redirects = self.followRedirects, withTemplateInclusion = self.withTemplateInclusion, onlyTemplateInclusion = self.onlyTemplateInclusion):
            yield page

class ReferringPagesGenerator:
    '''
    Yields all pages referring to a list of specific pages.
    '''
    def __init__(self, referredPages, followRedirects = False, withTemplateInclusion = True, onlyTemplateInclusion = False):
        self.referredPages = referredPages
        self.followRedirects = followRedirects
        self.withTemplateInclusion = withTemplateInclusion
        self.onlyTemplateInclusion = onlyTemplateInclusion

    def __iter__(self):
	allPages = []
	for referredPage in self.referredPages:
            for page in referredPage.getReferences(follow_redirects = self.followRedirects, withTemplateInclusion = self.withTemplateInclusion, onlyTemplateInclusion = self.onlyTemplateInclusion):
		allPages.append(page)

	#Remove duplicate pages.
	allPages = list(set(allPages))

	for page in allPages:
            yield page


class CategorizedPageGenerator:
    '''
    Yields all pages in a specific category.
    '''
    def __init__(self, category, recurse = False):
        self.category = category
        self.recurse = recurse

    def __iter__(self):
        for page in self.category.articles(recurse = self.recurse):
            yield page

class LinkedPageGenerator:
    '''
    Yields all pages linked from a specific page.
    '''
    def __init__(self, linkingPage):
        self.linkingPage = linkingPage

    def __iter__(self):
        for page in self.linkingPage.linkedPages():
            yield page

class TextfilePageGenerator:
    '''
    Read a file of page links between double-square-brackets, and return
    them as a list of Page objects. filename is the name of the file that
    should be read. If no name is given, the generator prompts the user.
    '''
    def __init__(self, filename = None):
        self.filename = filename or wikipedia.input(u'Please enter the filename:')

    def __iter__(self):
        site = wikipedia.getSite()
        f = codecs.open(self.filename, 'r', config.textfile_encoding)
        R = re.compile(r'\[\[(.+?)\]\]')
        for pageTitle in R.findall(f.read()):
            parts = pageTitle.split(':')
            i = 0
            try:
                fam = wikipedia.Family(parts[i], fatal = False)
                i += 1
            except:
                fam = site.family
            if parts[i] in fam.langs:
                code = parts[i]
                i += 1
            else:
                code = site.lang
            pagename = ':'.join(parts[i:])
            site = wikipedia.getSite(code = code, fam = fam)
            yield wikipedia.Page(site, pagename)
        f.close()

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
            wikipedia.output(u'Querying Google, offset %i' % offset) 
            data = google.doGoogleSearch(query, start = offset, filter = False)
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

class MySQLPageGenerator:
    '''

    '''
    def __init__(self, query):
        self.query = query
    
    def __iter__(self):
        import MySQLdb as mysqldb
        mysite = wikipedia.getSite()
        conn = mysqldb.connect(config.db_hostname, db = mysite.dbName(), user = config.db_username, passwd = config.db_password)
        cursor = conn.cursor()
        print repr(self.query)
        wikipedia.output(u'Executing query:\n%s' % self.query)
        self.query = self.query.encode(wikipedia.getSite().encoding())
        cursor.execute(self.query)
        while True:
            try:
                namespaceNumber, pageName = cursor.fetchone()
                print namespaceNumber, pageName
            except TypeError:
                # Limit reached or no more results
                break
            #print pageName
            if pageName:
                namespace = mysite.namespace(namespaceNumber)
                pageName = unicode(pageName, mysite.encoding())
                if namespace:
                    pageTitle = '%s:%s' % (namespace, pageName)
                else:
                    pageTitle = pageName
                page = wikipedia.Page(mysite, pageTitle)
                yield page

class YearPageGenerator:
    def __init__(self, start = 1, end = 2050):
        self.start = start
        self.end = end

    def __iter__(self):
        wikipedia.output(u"Starting with year %i" % self.start)
        for i in range(self.start, self.end + 1):
            if i % 100 == 0:
                wikipedia.output(u'Preparing %i...' % i)
            # There is no year 0
            if i != 0:
                current_year = date.formatYear(wikipedia.getSite().lang, i )
                yield wikipedia.Page(wikipedia.getSite(), current_year)

class DayPageGenerator:
    def __init__(self, startMonth = 1, endMonth = 12):
        self.startMonth = startMonth
        self.endMonth = endMonth

    def __iter__(self):
        fd = date.FormatDate(wikipedia.getSite())
        firstPage = wikipedia.Page(wikipedia.getSite(), fd(self.startMonth, 1))
        wikipedia.output(u"Starting with %s" % firstPage.aslink())
        for month in range(self.startMonth, self.endMonth+1):
            for day in range(1, date.getNumberOfDaysInMonth(month)+1):
                yield wikipedia.Page(wikipedia.getSite(), fd(month, day))

class NamespaceFilterPageGenerator:
    """
    Wraps around another generator. Yields only those pages that are in a list
    of specific namespace.
    """
    def __init__(self, generator, namespaces):
        """
        Parameters:
            * generator - the page generator around which this filter is
                          wrapped.
            * namespace - a list of namespace numbers.
        """
        self.generator = generator
        self.namespaces = namespaces

    def __iter__(self):
        for page in self.generator:
            if page.namespace() in self.namespaces:
                yield page

class RedirectFilterPageGenerator:
    """
    Wraps around another generator. Yields only those pages that are not redirects.
    """
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        for page in self.generator:
            if not page.isRedirectPage():
                yield page

class CombinedPageGenerator:
    """
    Wraps around a list of other generators. Yields all pages generated by the
    first generator; when the first generator stops yielding pages, yields those
    generated by the second generator, etc.
    """
    def __init__(self, generators):
        self.generators = generators

    def __iter__(self):
        for generator in self.generators:
            for page in generator:
                yield page

class PreloadingGenerator:
    """
    Wraps around another generator. Retrieves as many pages as stated by pageNumber
    from that generator, loads them using Special:Export, and yields them one after
    the other. Then retrieves more pages, etc.
    """
    def __init__(self, generator, pageNumber=60):
        self.generator = generator
        self.pageNumber = pageNumber

    def preload(self, pages):
        try:
            wikipedia.getall(wikipedia.getSite(), pages, throttle=False)
        except wikipedia.SaxError:
            # Ignore this error, and get the pages the traditional way later.
            pass

    def __iter__(self):
        # this array will contain up to pageNumber pages and will be flushed
        # after these pages have been preloaded and yielded.
        somePages = []
        i = 0
        for page in self.generator:
            i += 1
            somePages.append(page)
            # We don't want to load too many pages at once using XML export.
            # We only get a maximum number at a time.
            if i >= self.pageNumber:
                self.preload(somePages)
                for refpage in somePages:
                    yield refpage
                i = 0
                somePages = []
        # preload remaining pages
        self.preload(somePages)
        for refpage in somePages:
            yield refpage

