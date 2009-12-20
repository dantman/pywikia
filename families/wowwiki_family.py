# -*- coding: utf-8  -*-
import config, family, urllib

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wowwiki'

        self.langs = {
            'cs': 'cs.wow.wikia.com',
            'da': 'da.wowwiki.com',
            'de': 'de.wow.wikia.com',
            'el': 'el.wow.wikia.com',
            'en': 'www.wowwiki.com',
            'es': 'es.wow.wikia.com',
            'fa': 'fa.wow.wikia.com',
            'fi': 'fi.wow.wikia.com',
            'fr': 'fr.wowwiki.com',
            'he': 'he.wow.wikia.com',
            'hr': 'hr.wow.wikia.com',
            'hu': 'hu.wow.wikia.com',
            'is': 'is.wow.wikia.com',
            'it': 'it.wow.wikia.com',
            'ja': 'ja.wow.wikia.com',
            'ko': 'ko.wow.wikia.com',
            'lt': 'lt.wow.wikia.com',
            'lv': 'lv.wow.wikia.com',
            'nl': 'nl.wow.wikia.com',
            'no': 'no.wow.wikia.com',
            'pl': 'pl.wow.wikia.com',
            'pt-br': 'pt-br.wow.wikia.com',
            'pt': 'pt.wow.wikia.com',
            'ro': 'ro.wow.wikia.com',
            'ru': 'ru.wow.wikia.com',
            'sk': 'sk.wow.wikia.com',
            'sr': 'sr.wow.wikia.com',
            'sv': 'sv.warcraft.wikia.com',
            'tr': 'tr.wow.wikia.com',
            'zh-tw': 'zh-tw.wow.wikia.com',
            'zh': 'zh.wow.wikia.com'
        }

        self.namespaces[4] = {
            'cs': u'WoWWiki',
            'da': u'WoWWiki Danmark',
            'de': u'WoW-Wiki',
            'el': u'WoWWiki ????????? ?d????',
            'en': u'WoWWiki',
            'es': u'WarcraftWiki',
            'fa': u'????? ???????',
            'fi': u'WoWWiki Suomi',
            'fr': u'WikiWoW',
            'he': u'Worldofwiki',
            'hr': u'World of Warcraft Wiki',
            'hu': u'World of Warcraft Wiki',
            'is': u'WoWWiki',
            'it': u'WoWWiki Italia',
            'ja': u'World of Warcraft Wiki',
            'ko': u'World of Warcraft Wiki',
            'lt': u'World of Warcraft Wiki',
            'lv': u'World of Warcraft',
            'nl': u'WoWWiki',
            'no': u'Wowwiki Norge',
            'pl': u'WoWWiki',
            'pt': u'World of Warcraft',
            'pt-br': u'WowWiki Br',
            'ro': u'World of Warcraft Romania',
            'sk': u'WoWwiki',
            'sr': u'Wow wiki',
            'sv': u'WoWWiki Sverige',
            'ru': u'WoWWiki',
            'tr': u'Wow Tr Wikiame',
            'zh': u'World of Warcraft Wiki',
            'zh-tw': u'????????'
        }

        self.namespaces[5] = {
            'cs': u'WoWWiki diskuse',
            'da': u'WoWWiki Danmark-diskussion',
            'de': u'WoW-Wiki Diskussion',
            'el': u'WoWWiki ????????? ?d???? s???t?s?',
            'en': u'WoWWiki talk',
            'es': u'WarcraftWiki Discusión',
            'fa': u'??? ????? ???????',
            'fi': u'Keskustelu WoWWiki Suomista',
            'fr': u'Discussion WikiWoW',
            'he': u'???? Worldofwiki',
            'hr': u'Razgovor World of Warcraft Wiki',
            'hu': u'World of Warcraft Wiki-vita',
            'is': u'WoWWikispjall',
            'it': u'Discussioni WoWWiki Italia',
            'ja': u'World of Warcraft Wiki-???',
            'ko': u'World of Warcraft Wiki??',
            'lt': u'World of Warcraft Wiki aptarimas',
            'lv': u'World of Warcraft diskusija',
            'nl': u'Overleg WoWWiki',
            'no': u'Wowwiki Norge-diskusjon',
            'pl': u'Dyskusja WoWWiki',
            'pt': u'World of Warcraft Discussão',
            'pt-br': u'WowWiki Br Discussão',
            'ro': u'Discutie World of Warcraft Romania',
            'ru': u'?????????? WoWWiki',
            'sk': u'Diskusia k WoWwiki',
            'sr': u'???????? ? Wow wiki',
            'sv': u'WoWWiki Sverigediskussion',
            'tr': u'Wow Tr Wikiame tartisma',
            'zh': u'World of Warcraft Wiki talk',
            'zh-tw': u'??????????'
        }

        #wikia-wide defaults
        self.namespaces[110] = {
             '_default': 'Forum',
             'es': u'Foro',
             'fa': u'?????',
             'fi': u'Foorumi',
             'ru': u'?????'
        }
        self.namespaces[111] = {
             '_default': 'Forum talk',
             'es': u'Foro Discusión',
             'fa': u'??? ?????',
             'fi': u'Keskustelu foorumista',
             'pl': u'Dyskusja forum',
             'ru': u'?????????? ??????'
        }

        self.namespaces[400] = {
            '_default': u'Video',
            'ru': u'?????'
        }
        self.namespaces[401] = {
            '_default': u'Video talk',
            'ru': u'?????????? ?????'
        }
        self.namespaces[500] = { 
            '_default': u'User blog',
            'de': u'Benutzer Blog',
            'en': '', #disabled on en
            'ru': u'???? ?????????'
        }
        self.namespaces[501] = {
            '_default': u'User blog comment',
            'de': u'Benutzer Blog Kommentare',
            'en': '', #disabled on en
            'ru': u'??????????? ????? ?????????'
        }
        self.namespaces[502] = {
            '_default': u'Blog',
            'en': '', #disabled on en
            'ru': u'????'
        }
        self.namespaces[503] = {
            '_default': u'Blog talk',
            'de': u'Blog Diskussion',
            'en': '', #disabled on en
            'ru': u'?????????? ?????'
        }

        #a few edge cases:
        self.namespaces[112] = {
            'en': u'Guild', 'ru': u'??????'
        }
        self.namespaces[113] = {
            'en': u'Guild talk', 'ru': u'?????? talk'
        }
        self.namespaces[114] = {
            'en': u'Server', 'ru': u'???????'
        }
        self.namespaces[115] = {
            'en': u'Server talk', 'ru': u'??????? talk'
        }
        self.namespaces[116] = {
             'en': u'Portal', 'ru': u'??????'
        }
        self.namespaces[117] = {
            'en': u'Portal talk', 'ru': u'?????? talk'
        }

        #and a few more        
        self.namespaces[120] = { 'no': u'Oppdrag' }
        self.namespaces[121] = { 'no': u'Oppdrag Kommentar' }
        self.namespaces[122] = { 'no': u'Retningslinje' }
        self.namespaces[123] = { 'no': u'Retningslinje Kommentar' }
        self.namespaces[124] = { 'no': u'Portal' }
        self.namespaces[125] = { 'no': u'Portal diskusjon' }
        self.namespaces[126] = { 'no': u'Tinget' }
        self.namespaces[127] = { 'no': u'Tinget Diskusjon' }
        self.namespaces[128] = { 'no': u'Blogg' }
        self.namespaces[129] = { 'no': u'Blogg Kommentar' }

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
        return '1.15.1'

    def code2encoding(self, code):
        return 'utf-8'
