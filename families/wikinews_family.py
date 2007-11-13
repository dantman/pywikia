# -*- coding: utf-8  -*-

import urllib
import family, config

__version__ = '$Id$'

# The Wikimedia family that is known as WikiNews

# Known WikiNews languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikinews. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikinews'
        self.langs = {
      
            }
        
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikinews.org'
        
        # Override defaults
        self.namespaces[2]['pl'] = u'Wikireporter'
        self.namespaces[3]['pl'] = u'Dyskusja Wikireportera'

        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': [u'Wikinews', self.namespaces[4]['_default']],
            'ar': u'ويكي الأخبار',
            'bg': u'Уикиновини',
            'bs': u'Wikivijesti',
            'ca': u'Viquinotícies',
            'es': u'Wikinoticias',
            'he': u'ויקיחדשות',
            'it': u'Wikinotizie',
            'ja': u'ウィキニュース',
            'no': u'Wikinytt',
            'pt': u'Wikinotícias',
            'ro': u'Wikiştiri',
            'ru': u'ВикиНовости',
            'sr': u'Викивести',
            'th': u'วิกิข่าว',
            'uk': u'ВікіНовини',
        }
        self.namespaces[5] = {
            '_default': [u'Wikinews talk', self.namespaces[5]['_default']],
            'ar': u'نقاش ويكي الأخبار',
            'bg': u'Уикиновини беседа',
            'bs': u'Razgovor s Wikivijestima',
            'ca': u'Viquinotícies Discussió',
            'de': u'Wikinews Diskussion',
            'es': u'Wikinoticias Discusión',
            'fr': u'Discussion Wikinews',
            'he': u'שיחת ויקיחדשות',
            'it': u'Discussioni Wikinotizie',
            'ja': u'ウィキニュース‐ノート',
            'nl': u'Overleg Wikinews',
            'no': u'Wikinytt-diskusjon',
            'pl': u'Dyskusja Wikinews',
            'pt': u'Wikinotícias Discussão',
            'ro': u'Discuţie Wikiştiri',
            'ru': u'Обсуждение ВикиНовостей',
            'sr': u'Разговор о Викивестима',
            'sv': u'Wikinewsdiskussion',
            'ta': u'Wikinews பேச்சு',
            'th': u'คุยเรื่องวิกิข่าว',
            'uk': u'Обговорення ВікіНовини',
        }   
        
        self.namespaces[100] = {
            '_default': u'Portal',
            'he': u'פורטל',
            'it': u'Portale',
            'ja': u'ポータル',
            'zh': u'频道',
        }   

        self.namespaces[101] = {
            '_default': u'Portal talk',
            'he': u'שיחת פורטל',
            'it': u'Discussioni portale',
            'ja': u'ポータル‐ノート',
            'de': u'Portal Diskussion',
            'pl': u'Dyskusja portalu',
            'pt': u'Portal Discussão',
            'zh': u'频道 talk',
        }   

        self.namespaces[102] = {
            'fr': u'Transwiki',
            'pt': u'Efeméride',
        }   

        self.namespaces[103] = {
            'fr': u'Discussion Transwiki',
            'pt': u'Efeméride Discussão',
        }   

        self.namespaces[104] = {
            'fr': u'Page',
        }   

        self.namespaces[105] = {
            'fr': u'Discussion Page',
        }   

        self.namespaces[106] = {
            'fr': u'Dossier',
        }   

        self.namespaces[107] = {
            'fr': u'Discussion Dossier',
        }   

        self.namespaces[108] = {
            'ja': u'短信',
        }   

        self.namespaces[109] = {
            'ja': u'短信‐ノート',
        }   


        # On most Wikipedias page names must start with a capital letter, but some
        # languages don't use this.
            
        self.nocapitalize = ['cs', 'de', 'es', 'fa', 'fr', 'gu', 'hi', 'hr',
                        'hu', 'it', 'ja', 'ka', 'kn', 'ku', 'nl', 'sa',
                        'scn', 'sq', 'sv', 'sw', 'tokipona', 'tr', 'vi']
    
        self.obsolete = {'nb':'no',
                    'minnan':'zh-min-nan',
                    'zh-tw':'zh',
                    'zh-cn':'zh'}
    
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.
    
        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'fi': self.alphabetic,
            'fr': self.alphabetic,
            'he': ['en'],
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
            }

        self.languages_by_size = [
            'de', 'en', 'fr', 'gl', 'hu', 'it', 'ja', 'nl', 'pl', 'sv',
            'es', 'fi', 'hi', 'ko', 'la', 'pt', 'ru', 'tr', 'zh',
            'ca', 'eo', 'et', 'gu', 'he', 'hr', 'ro'
        ]
       
    def code2encoding(self, code):
        return 'utf-8'

    def version(self, code):
        return "1.11"
    
    def shared_image_repository(self, code):
        return ('commons', 'commons')
