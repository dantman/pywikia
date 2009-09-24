# -*- coding: utf-8  -*-
import config, family, urllib

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wowwiki'

        self.langs = {
            'en': 'www.wowwiki.com',
            'cs': 'cs.wow.wikia.com',
            'da': 'da.wowwiki.com',
            'de': 'de.wow.wikia.com',
            'el': 'el.wow.wikia.com',
            'es': 'es.wow.wikia.com',
            'fa': 'fa.wow.wikia.com',
            'fi': 'fi.wow.wikia.com',
            'fr': 'fr.wow.wikia.com',
            'he': 'he.wow.wikia.com',
            'hu': 'hu.wow.wikia.com',
            'is': 'is.wow.wikia.com',
            'it': 'it.wow.wikia.com',
            'ja': 'ja.wow.wikia.com',
            'ko': 'ko.wow.wikia.com',
            'lt': 'lt.wow.wikia.com',
            'lv': 'lv.wow.wikia.com',
            'nl': 'nl.wow.wikia.com',
            'nn': 'nn.wow.wikia.com',
            'no': 'no.wow.wikia.com',
            'pl': 'pl.wow.wikia.com',
            'pt': 'pt.wow.wikia.com',
            'pt-br': 'pt-br.wow.wikia.com',
            'ru': 'ru.wow.wikia.com',
            'sk': 'sk.wow.wikia.com',
            'zh': 'zh.wow.wikia.com',
            'zh-tw': 'zh-tw.wow.wikia.com',
        }

        self.namespaces[4] = {
            '_default': [u'Project', self.namespaces[4]['_default']],
            'en': 'WoWWiki',
            'de': 'WoW-Wiki',
            'es': 'WarcraftWiki',
            'fr': 'WikiWoW',
        }

        self.namespaces[5] = {
            'en': 'WoWWiki talk',
        }

        self.namespaces[110] = { '_default': 'Forum' }
        self.namespaces[111] = { '_default': 'Forum talk' }
        self.namespaces[112] = { '_default': 'Guild' }
        self.namespaces[113] = { '_default': 'Guild talk' }
        self.namespaces[114] = { '_default': 'Server' }
        self.namespaces[115] = { '_default': 'Server talk' }
        self.namespaces[116] = { '_default': 'Portal' }
        self.namespaces[117] = { '_default': 'Portal talk' }
        self.namespaces[400] = { '_default': 'Video' }
        self.namespaces[401] = { '_default': 'Video talk' }

        self.content_id = "article"

        self.disambiguationTemplates['en'] = ['disambig', 'disambig/quest', 'disambig/quest2', 'disambig/achievement2']
        self.disambcatname['en'] = "Disambiguations"

    def protocol(self, code):
        return 'http'

    def scriptpath(self, code):
        return ''

    def apipath(self, code):
        return '%s/api.php' % self.scriptpath(code)

    def version(self, code):
        # Replace with the actual version being run on your wiki
        return '1.15.1'

    def code2encoding(self, code):
        return 'utf-8'
