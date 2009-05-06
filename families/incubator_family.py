# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family, config

# The Wikimedia Incubator family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'incubator'
        self.langs = {
            'incubator': 'incubator.wikimedia.org',
        }
        if config.SSL_connection and self.name in config.available_ssl_project:
            self.langs['incubator'] = 'secure.wikimedia.org'

        self.namespaces[4] = {
            '_default': [u'Incubator', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Incubator talk', self.namespaces[5]['_default']],
        }
        self.namespaces[100] = {
            '_default': u'Lost',
        }
        self.namespaces[101] = {
            '_default': u'Lost talk',
        }

    def version(self, code):
        return '1.15alpha'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def scriptpath(self, code):
        if config.SSL_connection and self.name in config.available_ssl_project:
            return '/wikipedia/incubator/w'
        
        return '/w'
