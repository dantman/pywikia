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
        if config.SSL_connection and self.name in config.available_ssl_project:
            self.langs['species'] = 'secure.wikimedia.org'

        self.namespaces[4] = {
            '_default': [u'Wikispecies', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikispecies talk', self.namespaces[5]['_default']],
        }

        self.interwiki_forward = 'wikipedia'

    def version(self,code):
        return '1.16alpha'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def scriptpath(self, code):
        if config.SSL_connection and self.name in config.available_ssl_project:
            return '/wikipedia/species/w'

        return '/w'
