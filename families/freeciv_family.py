# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The project wiki of Freeciv, an open source strategy game.

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'freeciv'
        self.langs = {
            'da': 'da.freeciv.wikia.com',
            'de': 'de.freeciv.wikia.com',
            'en': 'freeciv.wikia.com',
            'es': 'es.freeciv.wikia.com',
            'fi': 'fi.freeciv.wikia.com',
            'fr': 'fr.freeciv.wikia.com',
        }
        
        self.namespaces[4] = {
            '_default': [u'Freeciv', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Freeciv talk', self.namespaces[5]['_default']],
            'fr': u'Discussion Freeciv',
            'de': u'Freeciv Diskussion',
        }

        self.namespaces[110] = {
            '_default': u'Forum',
        }

        self.namespaces[111] = {
            '_default': u'Forum talk',
        }


    def path(self, code):
        return '/index.php'

    def version(self, code):
        return "1.9.2"
