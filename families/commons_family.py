# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family, config

# The Wikimedia Commons family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'commons'
        self.langs = {
            'commons': 'commons.wikimedia.org',
        }
        if config.SSL_connection and self.name in config.available_ssl_project:
            self.langs['commons'] = 'secure.wikimedia.org'

        self.namespaces[4] = {
            '_default': [u'Commons', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Commons talk', self.namespaces[5]['_default']],
        }
        self.namespaces[100] = {
            '_default': [u'Creator', self.namespaces[5]['_default']],
        }
        self.namespaces[101] = {
            '_default': [u'Creator talk', self.namespaces[5]['_default']],
        }

        self.interwiki_forward = 'wikipedia'

        self.category_redirect_templates = {
            'commons': (u'Category redirect',
                        u'Categoryredirect',
                        u'See cat',
                        u'Seecat',
                        u'Catredirect',
                        u'Cat redirect',
                        u'CatRed',
                        u'Cat-red',
                        u'Catredir',
                        u'Redirect category'),
        }
        
        self.disambiguationTemplates = {
            'commons': [u'Disambig', u'Disambiguation', u'Razločitev',
                        u'Begriffsklärung']
        }
        
        self.disambcatname = {
            'commons':  u'Disambiguation'
        }

    def version(self, code):
        return '1.15alpha'

    def dbName(self, code):
        return 'commonswiki_p'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    def scriptpath(self, code):
        if config.SSL_connection and self.name in config.available_ssl_project:
            return '/wikipedia/commons/w'

        return '/w'
