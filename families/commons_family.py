# -*- coding: utf-8  -*-

import family

# The Wikimedia Commons family

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'commons'
        self.langs = {
            'commons': 'commons.wikimedia.org',
        }
        
        self.namespaces[4] = {
            '_default': 'Commons',
        }
        self.namespaces[5] = {
            '_default': 'Commons talk',
        }
