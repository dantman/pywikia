#!/usr/bin/python
# -*- coding: utf-8  -*-

import wikipedia

class SinglePageGenerator:
    '''Pseudo-generator'''
    def __init__(self, pl):
        self.pl = pl

    def generate(self):
        yield self.pl

class AllpagesPageGenerator:
    '''
    Using the Allpages special page, retrieves all articles, loads them (60 at
    a time) using XML export, and yields title/text pairs.
    '''
    def __init__(self, start ='!'):
        self.start = start
    
    def generate(self):
        for page in wikipedia.allpages(start = self.start):
            yield page

class PreloadingGenerator:
    """
    Wraps around another generator. Retrieves up to 20 pages from that
    generator, loads them using Special:Export, and yields them one after
    the other. Then retrieves 20 more pages, etc.
    """
    def __init__(self, generator, pageNumber = 60):
        self.generator = generator
        self.pageNumber = pageNumber

    def preload(self, pages):
        try:
            wikipedia.getall(wikipedia.getSite(), pages, throttle=False)
        except wikipedia.SaxError:
            # Ignore this error, and get the pages the traditional way later.
            pass
        
    def generate(self):
        # this array will contain up to 20 pages and will be flushed
        # after these pages have been preloaded.
        somePages = []
        i = 0
        for page in self.generator.generate():
            i += 1
            somePages.append(page)
            # We don't want to load too many pages at once using XML export.
            # We only get 20 at a time.
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

