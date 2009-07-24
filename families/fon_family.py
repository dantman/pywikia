# -*- coding: utf-8  -*-

import family

# The official Beta Wiki.
class Family(family.Family):

    def __init__(self):

        family.Family.__init__(self)
        self.name = 'fon'

        self.langs = {
            'en': None,
        }

        self.namespaces[4] = {
            '_default': u'FON Wiki Beta',
        }

        self.namespaces[5] = {
            '_default': u'FON Wiki Beta talk',
        }

        self.namespaces[6] = {
            '_default': u'Image',
        }

        self.namespaces[7] = {
            '_default': u'Image talk',
        }

    def hostname(self, code):
        return 'wiki.fon.com'

    def scriptpath(self, code):
        return '/mediawiki'

    def version(self, code):
        return "1.12.1" 