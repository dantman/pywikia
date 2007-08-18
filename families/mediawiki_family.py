# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The MediaWiki family
# user-config.py: usernames['mediawiki']['mediawiki'] = 'User name'


class Family(family.Family):
    def __init__(self):

        family.Family.__init__(self)
        self.name = 'mediawiki'

        self.langs = {
            'mediawiki': 'www.mediawiki.org',
        }
        
        self.namespaces[4] = {
            '_default': [u'Project', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Project talk', self.namespaces[5]['_default']],
        }

    def version(self, code):
        return "1.11"
    def shared_image_repository(self, code):
        return ('commons', 'commons')
s