# -*- coding: utf-8  -*-

import family

# The meta family

class Family(family.Family):
    name = 'meta'
    def __init__(self):
    	self._addlang('meta',
			location = 'meta.wikimedia.org',
			namespaces = { 4: u'Meta',
			              5: u'Meta talk' })
