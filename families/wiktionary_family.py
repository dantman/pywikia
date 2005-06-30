# -*- coding: utf-8  -*-

import urllib
import family, config

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

        self.nocapitalize = ['cs', 'de', 'en', 'eo', 'es', 'fa', 'fr', 'gu',
                        'hi', 'hr', 'hu', 'it', 'ja', 'ka', 'kn', 'ku', 'nl',
                        'sa', 'scn', 'sq', 'sv', 'sw', 'tlh', 'tokipona',
                        'tr', 'vi']
    
        self.obsolete = {'no':'nb',
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
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
            }
            
        # group of languages that we might want to do at once
    
        self.biglangs = ['de', 'en', 'fr', 'gl', 'hu', 'it', 'ja', 'nl', 'pl', 'sv']
                    
        self.biglangs2 = self.biglangs + [
            'es', 'fi', 'hi', 'ko', 'la', 'pt', 'ru', 'tr', 'zh']
        
        self.biglangs3 = self.biglangs2 + [
            'ca', 'eo', 'et', 'gu', 'he', 'hr', 'ro']
        
        self.biglangs4 = self.biglangs3
                    
        self.seriouslangs = self.biglangs4
        
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic