# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family, config

# The Wikimedia Strategy family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'strategy'
        self.langs = {
            'strategy': 'strategy.wikimedia.org',
        }
        if config.SSL_connection:
            self.langs['commons'] = None

        self.namespaces[4] = {
            '_default': [u'Strategic Planning', 'Project'],
        }
        self.namespaces[5] = {
            '_default': [u'Strategic Planning talk', 'Project talk'],
        }
        self.namespaces[100] = {
            '_default': [u'Creator', 'Project'],
        }
        self.namespaces[101] = {
            '_default': [u'Creator talk', 'Project talk'],
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
        return '1.16alpha-wmf'

    def dbName(self, code):
        return 'strategywiki_p'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    if config.SSL_connection:
        def hostname(self, code):
            return 'secure.wikimedia.org'

        def protocol(self, code):
            return 'https'

        def scriptpath(self, code):
            return '/wikipedia/strategy/w'

        def nicepath(self, code):
            return '/wikipedia/strategy/wiki/'
