# -*- coding: utf-8  -*-

import family

# The meta family

class Family(family.Family):
    name = 'meta'
    def __init__(self):
        self.langs = {
            'meta': 'meta.wikimedia.org',
        }
        
        self.namespaces[4] = {
            '_default': 'Meta',
        }
        self.namespaces[5] = {
            '_default': 'Meta talk',
        }