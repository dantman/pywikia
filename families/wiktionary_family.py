# -*- coding: utf-8  -*-

import urllib
import family, config

__version__ = '$Id$'

# The Wikimedia family that is known as Wiktionary

# Known wiktionary languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wiktionary. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wiktionary'
        self.langs = {
            'minnan':'zh-min-nan.wiktionary.org',
            'nb':'no.wiktionary.org',
            'zh-cn':'zh.wiktionary.org',
            'zh-tw':'zh.wiktionary.org'
            }
        
        for lang in self.knownlanguages:
            if not lang in ['ee','ht','ny', 'se', 'tum']:
                self.langs[lang] = lang+'.wiktionary.org'
        
        # Most namespaces are inherited from family.Family.

        self.namespaces[4] = {
            '_default': [u'Wiktionary', self.namespaces[4]['_default']],
            'ar': u'ويكيبيديا',
            'bg': u'Уикиречник',
            'bn': u'উইকিপেডিয়া',
            'csb': u'Wiki',
            'eo': u'Vikivortaro',
            'es': u'Wikcionario',
            'et': u'Vikisõnaraamat',
            'fi': u'Wikisanakirja',
            'fo': u'Wiktionary',
            'fr': u'Wiktionnaire',
            'ga': u'Vicipéid',
            'gu': u'વિક્ષનરી',
            'he': u'ויקימילון',
            'hi': u'विक्षनरी',
            'hu': u'Wikiszótár',
            'is': u'Wikiorðabók',
            'ka': u'ვიქსიკონი',
            'ko': u'위키낱말사전',
            'la': u'Victionarium',
            'ms': u'Wiktionary',
            'nl': u'WikiWoordenboek',
            'oc': u'Oiquipedià',
            'pl': u'Wikisłownik',
            'pt': u'Wikcionário',
            'ru': u'Викисловарь',
            'sk': u'Wikislovník',
            'sl': u'Wikipedija',
            'sr': u'Викиречник',
            'tr': u'Vikisözlük',
            'tt': u'Wiktionary',
            'yi': u'װיקיװערטערבוך',
        }
        
        self.namespaces[5] = {
            '_default': [u'Wiktionary talk', self.namespaces[5]['_default']],
            'ab': u'Обсуждение Wiktionary',
            'af': u'Wiktionarybespreking',
            'als': u'Wiktionary Diskussion',
            'ar': u'نقاش ويكيبيديا',
            'ast': u'Wiktionary discusión',
            'av': u'Обсуждение Wiktionary',
            'ay': u'Wiktionary Discusión',
            'ba': u'Обсуждение Wiktionary',
            'be': u'Абмеркаваньне Wiktionary',
            'bg': u'Уикиречник беседа',
            'bm': u'Discussion Wiktionary',
            'bn': u'উইকিপেডিয়া আলাপ',
            'br': u'Kaozeadenn Wiktionary',
            'ca': u'Wiktionary Discussió',
            'cs': u'Wiktionary diskuse',
            'csb': u'Diskùsëjô Wiki',
            'cy': u'Sgwrs Wiktionary',
            'da': u'Wiktionary diskussion',
            'de': u'Wiktionary Diskussion',
            'el': u'Wiktionary συζήτηση',
            'eo': u'Vikivortaro diskuto',
            'es': u'Wikcionario Discusión',
            'et': u'Vikisõnaraamat arutelu',
            'eu': u'Wiktionary eztabaida',
            'fa': u'بحث Wiktionary',
            'fi': u'Keskustelu Wikisanakirjasta',
            'fo': u'Wiktionary kjak',
            'fr': u'Discussion Wiktionnaire',
            'fy': u'Wiktionary oerlis',
            'ga': u'Plé Vicipéide',
            'gn': u'Wiktionary Discusión',
            'gu': u'વિક્ષનરી talk',
            'he': u'שיחת ויקימילון',
            'hi': u'विक्षनरी वार्ता',
            'hr': u'Razgovor Wiktionary',
            'hu': u'Wikiszótár vita',
            'ia': u'Discussion Wiktionary',
            'id': u'Pembicaraan Wiktionary',
            'is': u'Wikiorðabókspjall',
            'it': u'Discussioni Wiktionary',
            'ja': u'Wiktionary‐ノート',
            'ka': u'ვიქსიკონი განხილვა',
            'ko': u'위키낱말사전토론',
            'ku': u'Wiktionary nîqaş',
            'la': u'Disputatio Victionarii',
            'li': u'Euverlik Wiktionary',
            'lt': u'Wiktionary aptarimas',
            'mk': u'Wiktionary разговор',
            'ms': u'Perbualan Wiktionary',
            'nds': u'Wiktionary Diskuschoon',
            'nl': u'Overleg WikiWoordenboek',
            'nn': u'Wiktionary-diskusjon',
            'no': u'Wiktionary-diskusjon',
            'oc': u'Discutida Oiquipedià',
            'pa': u'Wiktionary ਚਰਚਾ',
            'pl': u'Wikidyskusja',
            'pt': u'Wikcionário Discussão',
            'qu': u'Wiktionary Discusión',
            'ro': u'Discuţie Wiktionary',
            'ru': u'Обсуждение Викисловаря',
            'sc': u'Wiktionary discussioni',
            'sk': u'Diskusia k Wikislovníku',
            'sl': u'Pogovor k Wikipediji',
            'sq': u'Wiktionary diskutim',
            'sr': u'Разговор о викиречнику',
            'sv': u'Wiktionarydiskussion',
            'ta': u'Wiktionary பேச்சு',
            'tr': u'Vikisözlük tartışma',
            'tt': u'Wiktionary bäxäse',
            'uk': u'Обговорення Wiktionary',
            'vi': u'Thảo luận Wiktionary',
            'wa': u'Wiktionary copene',
            'yi': u'װיקיװערטערבוך רעדן',
        }

        self.namespaces[100] = {
            '_default': u'Appendix',
            'bg': u'Словоформи',
            'fr': u'Annexe',
            'pl': u'Aneks'
        }
        self.namespaces[101] = {
            '_default': u'Appendix talk',
            'bg': u'Словоформи беседа',
            'fr': u'Discussion Annexe',
            'pl': u'Dyskusja aneksu'
        }
        self.namespaces[102] = {
            '_default': u'Concordance',
            'de': u'Verzeichnis',
            'fr': u'Transwiki',
            'pl': u'Indeks'
        }
        self.namespaces[103] = {
            '_default': u'Concordance talk',
            'de': u'Verzeichnis Diskussion',
            'fr': u'Discussion Transwiki',
            'pl': u'Dyskusja indeksu'
        }
        self.namespaces[104] = {
            '_default': u'Index',
        }
        self.namespaces[105] = {
            '_default': u'Index talk',
        }


        # Other than most Wikipedias, page names must not start with a capital
        # letter on ALL Wiktionaries.

        self.nocapitalize = self.langs.keys()
    
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
            'et': self.alphabetic,
            'fi': self.alphabetic,
            'fr': self.alphabetic,
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
            }
            
        self.languages_by_size = [
            'en', 'fr', 'vi', 'zh', 'io', 'el', 'pl', 'it', 'de', 'hu',
            'fi', 'nl', 'bg', 'pt', 'ku', 'es', 'gl', 'sr', 'id', 'sv',
            'et', 'ru', 'ko', 'tr', 'ja', 'sl', 'scn', 'fa', 'ar', 'no',
            'la', 'ta', 'zh-min-nan', 'he', 'hy', 'af', 'ro', 'da', 'ang', 'hi',
            'cs', 'sk', 'is', 'uk', 'co', 'ca', 'simple', 'st', 'fy', 'hr',
            'nds', 'csb', 'ky', 'kk', 'ia', 'gu', 'sq', 'sd', 'eo', 'lt',
            'cy', 'vo', 'ml', 'ie', 'th', 'yi', 'mk', 'bs', 'qu', 'am',
            'mr', 'be', 'rw', 'tl', 'eu', 'ms', 'ast', 'an', 'ga', 'pa',
            'nah', 'ha', 'oc'
            ]
        
        self.interwiki_on_one_line = ['pl']

        self.interwiki_attop = ['pl']

    def version(self, code):
        return "1.11"
    
    def shared_image_repository(self):
        return ('commons', 'commons')

