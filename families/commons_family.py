# -*- coding: utf-8  -*-

import family

# The Wikimedia Commons family

class Family(family.Family):
    name = 'commons'
    def __init__(self):
        self.langs = {
            'commons': 'commons.wikimedia.org',
        }
        
        self.namespaces[4] = {
            '_default': 'Commons',
        }
        self.namespaces[5] = {
            '_default': 'Commons talk',
        }    def __init__(self):
