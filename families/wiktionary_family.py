# -*- coding: utf-8  -*-

import urllib
import family, config

__version__ = ''

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
            '_default': u'Wiktionary',
        }
        self.namespaces[5] = {
            '_default': u'Wiktionary talk',
            'de': u'Wiktionary Diskussion',
            'pt': u'Wiktionary Discussão',
            'es': u'Wiktionary Discusión',
        }

        # Other than most Wikipedias, page names must not start with a capital
        # letter on some Wiktionaries.

        self.nocapitalize = ['af', 'bg', 'cs', 'de', 'en', 'eo', 'es',
                        'fa', 'fi', 'fr', 'gu', 'hi', 'hr', 'hu', 'is', 'it',
                        'ja', 'ka', 'kn', 'ku', 'ml', 'nds', 'nl', 'pl',
                        'sa', 'scn', 'sq', 'sv', 'sw', 'tg', 'tlh', 'tokipona',
                        'tr', 'vi']
    
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
            
        # group of languages that we might want to do at once
    
        self.languages_by_size = [
            'bg', 'bg', 'fr', 'gl', 'hu', 'io', 'it', 'nl', 'pl', 'scn',
            'de', 'es', 'et', 'fi', 'hi', 'ku', 'ja', 'la', 'pt', 'sv',
            'ang', 'co', 'da', 'gu', 'hr', 'ko', 'no', 'ru', 'tr', 'zh',
            'ar', 'bs', 'ca', 'cs', 'el', 'eo', 'eu', 'he', 'ia', 'id',
            'ie', 'ro', 'sr', 'ta', 'th', 'uk', 'vi'
        ]
        
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic

        self.interwiki_on_one_line = ['pl']

        self.interwiki_attop = ['pl']
