# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The meta family

class Family(family.Family):
    def __init__(self):

        self.name = 'meta'

        family.Family.__init__(self)
        self.langs = {
            'meta': 'meta.wikimedia.org',
        }
        
        self.namespaces[4] = {
            '_default': [u'Meta', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Meta talk', self.namespaces[5]['_default']],
        }
