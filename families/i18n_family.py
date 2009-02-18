# -*- coding: utf-8  -*-

__version__ = '$Id: incubator_family.py 4068 2007-08-18 13:10:09Z btongminh $'

import family

# The Wikimedia i18n family (should be called Betawiki, but already exists)

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'i18n'
        self.langs = {
            'i18n': 'translatewiki.net',
        }

        self.namespaces[4] = {
            '_default': [u'Project'],
        }
        self.namespaces[5] = {
            '_default': [u'Project talk'],
        }
        self.namespaces[6] = {
            '_default': [u'File'],
        }
        self.namespaces[7] = {
            '_default': [u'File talk'],
        }
        self.namespaces[100] = {
            '_default': [u'Portal'],
        }
        self.namespaces[101] = {
            '_default': [u'Portal talk'],
        }
        self.namespaces[1102] = {
            '_default': [u'Translating'],
        }
        self.namespaces[1103] = {
            '_default': [u'Translating talk'],
        }
        self.namespaces[1200] = {
            '_default': [u'Voctrain'],
        }
        self.namespaces[1201] = {
            '_default': [u'Voctrain talk'],
        }
        self.namespaces[1202] = {
            '_default': [u'FreeCol'],
        }
        self.namespaces[1203] = {
            '_default': [u'FreeCol talk'],
        }
        self.namespaces[1210] = {
            '_default': [u'Mantis'],
        }
        self.namespaces[1211] = {
            '_default': [u'Mantis talk'],
        }
        self.namespaces[1212] = {
            '_default': [u'Mwlib'],
        }
        self.namespaces[1213] = {
            '_default': [u'Mwlib talk'],
        }
        self.namespaces[1214] = {
            '_default': [u'Commonist'],
        }
        self.namespaces[1215] = {
            '_default': [u'Commonist talk'],
        }

    def version(self, code):
        return "1.15alpha"
