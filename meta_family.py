# -*- coding: utf-8  -*-

import config, urllib, family

# The meta family

# Known wikipedia languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikipedia. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):
    def __init__(self):
        self._addlang(code = 'meta',
                      location = 'meta.wikimedia.org',
                      namespaces = {-2 : u'Media',
                                    -1 : u'Special',
                                    0  : None,
                                    1 : u'Talk',
                                    2 : u'User',
                                    3 : u'User talk',
                                    4 : u'Wikipedia',
                                    5 : u'Wikipedia talk',
                                    6 : u'Image',
                                    7 : u'Image talk',
                                    8 : u'MediaWiki',
                                    9 : u'MediaWiki talk',
                                    10 : u'Template',
                                    11 : u'Template talk',
                                    12 : u'Help',
                                    13 : u'Help talk',
                                    14 : u'Category',
                                    15 : u'Category talk'})
        
