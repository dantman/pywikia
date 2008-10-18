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
            '_default': [u'Betawiki'],
        }
        self.namespaces[5] = {
            '_default': [u'Betawiki talk'],
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
        self.namespaces[1204] = {
            '_default': [u'Deprecated1'],
        }
        self.namespaces[1205] = {
            '_default': [u'Deprecated1 talk'],
        }
        self.namespaces[1206] = {
            '_default': [u'Deprecated2'],
        }
        self.namespaces[1207] = {
            '_default': [u'Deprecated2 talk'],
        }
        self.namespaces[1208] = {
            '_default': [u'Zabbix'],
        }
        self.namespaces[1209] = {
            '_default': [u'Zabbix talk'],
        }
        self.namespaces[1210] = {
            '_default': [u'Mantis'],
        }
        self.namespaces[1211] = {
            '_default': [u'Mantis talk'],
        }
        self.namespaces[9900] = {
            '_default': [u'Translations'],
        }
        self.namespaces[9901] = {
            '_default': [u'Translations talk'],
        }

    def version(self, code):
        return "1.14alpha"
