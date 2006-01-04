#!/usr/bin/python
# -*- coding: utf-8  -*-

__version__='$Id:'

# Standard library imports
import re, codecs

# Application specific imports
import wikipedia, date
import config

class AllpagesPageGenerator:
    '''
    Using the Allpages special page, retrieves all articles, loads them (60 at
    a time) using XML export, and yields title/text pairs.
    '''
    def __init__(self, start ='!', namespace = 0):
        self.start = start
        self.namespace = namespace

    def __iter__(self):
        for page in wikipedia.getSite().allpages(start = self.start, namespace = self.namespace):
            yield page

class ReferringPageGenerator:
    '''
    Yields all pages referring to a specific page.
    '''
    def __init__(self, referredPage, followRedirects = False):
        self.referredPage = referredPage
        self.followRedirects = followRedirects

    def __iter__(self):
        for page in self.referredPage.getReferences(follow_redirects = self.followRedirects):
            yield page

AllReferringPageGenerator = ReferringPageGenerator
# line above included for backwards compatibility

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
    them as a list of Page objects. 'filename' is the name of the file that
    should be read.
    '''
    def __init__(self, filename):
        self.filename = filename

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
            for day in range(1, date.days_in_month[month]+1):
                yield wikipedia.Page(wikipedia.getSite(), fd(month, day))

class NamespaceFilterPageGenerator:
    def __init__(self, generator, namespaces):
        self.generator = generator
        self.namespaces = namespaces

    def __iter__(self):
        for page in self.generator:
            if page.namespace() in self.namespaces:
                yield page

class CombinedGenerator:
    def __init__(self,generator1,generator2):
        self.gen1 = generator1
        self.gen2 = generator2

    def __iter__(self):
        for page in self.gen1:
            yield page
        for page in self.gen2:
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
        # after these pages have been preloaded.
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

