# -*- coding: utf-8  -*-

__version__ = '$Id$'

import family

# The project wiki of Freeciv, an open source strategy game.

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'freeciv'
        self.langs = {
            'ca': 'ca.freeciv.wikia.com',
            'da': 'da.freeciv.wikia.com',
            'de': 'de.freeciv.wikia.com',
            'en': 'freeciv.wikia.com',
            'es': 'es.freeciv.wikia.com',
            'fi': 'fi.freeciv.wikia.com',
            'fr': 'fr.freeciv.wikia.com',
            'ja': 'ja.freeciv.wikia.com',
            'ru': 'ru.freeciv.wikia.com',
        }

        self.namespaces[1]['fr'] = u'Discuter'

        self.namespaces[3]['fr'] = u'Discussion Utilisateur'

        self.namespaces[4] = {
            '_default': u'Freeciv',
            'fi': u'FreeCiv wiki Suomalaisille',
            'ja': u'Freeciv.org ジャパン',
        }

        self.namespaces[5] = {
            '_default': u'Freeciv talk',
            'ca': u'Freeciv Discussió',
            'da': u'Freeciv-diskussion',
            'de': u'Freeciv Diskussion',
            'es': u'Freeciv Discusión',
            'fi': u'Keskustelu FreeCiv wiki Suomalaisillesta',
            'fr': u'Discussion Freeciv',
            'ja': u'Freeciv.org ジャパン‐ノート',
            'ru': u'Обсуждение Freeciv',
        }

        self.namespaces[6]['da'] = u'Billede'

        self.namespaces[7]['da'] = u'Billeddiskussion'
        self.namespaces[7]['fr'] = u'Discussion Fichier'

        self.namespaces[8]['fi'] = u'Järjestelmäviesti'

        self.namespaces[11]['fr'] = u'Discussion Modèle'

        self.namespaces[13]['fr'] = u'Discussion Aide'

        self.namespaces[15]['fr'] = u'Discussion Catégorie'

        self.namespaces[110] = {
            '_default': u'Forum',
            'fi': u'Foorumi',
            'ru': u'Форум',
        }

        self.namespaces[111] = {
            '_default': u'Forum talk',
            'fi': u'Keskustelu foorumista',
            'ru': u'Обсуждение форума',
        }
        self.namespaces[400] = {
            '_default': u'Video',
        }

        self.namespaces[401] = {
            '_default': u'Video talk',
        }


    def scriptpath(self, code):
        return ''

    def version(self, code):
        return "1.10alpha"
