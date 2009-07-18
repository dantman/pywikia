# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family, config

# The wikispecies family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'species'
        self.langs = {
            'species': 'species.wikimedia.org',
        }
        if config.SSL_connection:
            self.langs['species'] = None

        self.namespaces[4] = {
            '_default': [u'Wikispecies', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikispecies talk', self.namespaces[5]['_default']],
        }

        self.interwiki_forward = 'wikipedia'

    def version(self,code):
        return '1.16alpha-wmf'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    if config.SSL_connection:
        def hostname(self, code):
            return 'secure.wikimedia.org'

        def protocol(self, code):
            return 'https'

        def scriptpath(self, code):
            return '/wikipedia/species/w'

        def nicepath(self, code):
            return '/wikipedia/species/wiki/'
