# -*- coding: utf-8  -*-

import family

# The test family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'test'
        self.langs = {
            'test': 'test.wikipedia.org',
           }
        
        self.namespaces[4] = {
            '_default': [u'Wikipedia', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikipedia talk', self.namespaces[5]['_default']],
        }
