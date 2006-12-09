# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The Wikimedia Incubator family

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'supertux'
        self.langs = {
            'en': 'supertux.berlios.de',
        }
        
        self.namespaces[4] = {
            '_default': [u'Incubator', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Incubator talk', self.namespaces[5]['_default']],
        }

    def path(self, code):
        return '/wiki/index.php'

    def querypath(self, code):
        return '/wiki/query.php'


    def version(self, code):
        return "1.5"

