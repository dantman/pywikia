# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as Wikibooks

class Family(family.Family):
    name = 'mozilla'
    def __init__(self):
        for lang in ['en','nl']:
            self._addlang('lang',
			location = 'wiki.mozilla.org',
			namespaces = { 4: u'MozillaWiki',
			              5: u'MozillaWiki talk' })
