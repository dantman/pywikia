# -*- coding: utf-8  -*-

import urllib
import family, config

__version__ = '$Id$'

# An inofficial Gentoo wiki project

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'gentoowiki'

        self.langs = {
            'en':'gentoo-wiki.com',
            'nl':'nl.gentoo-wiki.com',
            'hu':'hu.gentoo-wiki.com',
            'ru':'ru.gentoo-wiki.com',
            'zh':'zh.gentoo-wiki.com',
            'he':'he.gentoo-wiki.com',
            'fr':'fr.gentoo-wiki.com',
            'de':'de.gentoo-wiki.com',
            'es':'es.gentoo-wiki.com',
            'pt':'pt.gentoo-wiki.com',
        }

        self.namespaces[4] = {
            '_default': [u'Gentoo Linux Wiki', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Gentoo Linux Wiki talk', self.namespaces[5]['_default']],
            'de': u'Gentoo Linux Wiki Diskussion',
        }
        self.namespaces[100] = {
            '_default': [u'Index'],
        }
        self.namespaces[101] = {
            '_default': [u'Index Talk'],
        }
        self.namespaces[110] = {
            '_default': [u'Ucpt'],
        }
        self.namespaces[111] = {
            '_default': [u'Ucpt talk'],
        }


    def path(self, code):
        return '/index.php'

    def version(self, code):
        return "1.9alpha"