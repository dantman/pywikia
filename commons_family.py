# -*- coding: utf-8  -*-

import family

# The commons family

class Family(family.Family):
    name = 'commons'
    def __init__(self):
    	self._addlang('commons',
			location = 'commons.wikimedia.org',
			namespaces = { 4: u'Commons',
			              5: u'Commons talk' })
