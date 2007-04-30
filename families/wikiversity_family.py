# -*- coding: utf-8  -*-
import urllib
import family, config

__version__ = '$Id$'

# The wikimedia family that is known as Wikiversity

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikiversity'

        for lang in self.knownlanguages:
            if lang not in self.langs:
                self.langs[lang] = lang+'.wikiversity.org'
		    
        self.namespaces[4] = {
            '_default': [u'Wikiversity', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikiversity talk', self.namespaces[5]['_default']],
        }
