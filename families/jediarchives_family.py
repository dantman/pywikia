# -*- coding: utf-8  -*-

import family

# Jedi Archives, a Star Wars wiki.

class Family(family.Family):
    name = 'jediarchives'
    
    def __init__(self):
        family.Family.__init__(self)
	self.langs = {
            'en': 'jediarchives.info',
	}
	self.namespaces[4] = {
	    '_default': u'JediArchives',
	    }
	self.namespaces[5] = {
	    '_default': u'JediArchives talk',
	    }
	
    def version(self, code):
        return "1.5.3"
    
    def path(self, code):
        return '/wiki/index.php'

