# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as Wikibooks

class Family(family.Family):
    name = 'mozilla'
    def __init__(self):
        for lang in ['en','nl']:
            self._addlang(lang,
			location = 'wiki.mozilla.org',
			namespaces = {-2: u'Media',
                                      -1: u'Special',
                                      0: None,
                                      1: u'Talk',
                                      2: u'User',
                                      3: u'User talk',
                                      4: u'MozillaWiki',
			              5: u'MozillaWiki talk',
                                      6: u'Image',
                                      7: u'Image talk',
                                      8: u'MediaWiki',
                                      9: u'MediaWiki talk',
                                      10: u'Template',
                                      11: u'Template talk',
                                      12: u'Help',
                                      13: u'Help talk',
                                      14: u'Category',
                                      15: u'Category talk'})
    def version(self, code):
        return "1.3.8"
    
    def path(self, code):
        return '/wiki'
