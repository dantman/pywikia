# -*- coding: utf-8  -*-

import urllib
import family, config

# The Wikimedia family that is known as Wikipedia, the Free Encyclopedia

class Family(family.Family):
    
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikipedia'

        self.langs = {
            'dk':'da.wikipedia.org',
            'jp':'ja.wikipedia.org',
            'minnan':'zh-min-nan.wikipedia.org',
            'nb':'no.wikipedia.org',
            'tokipona':'tokipona.wikipedia.org',
            'sh':'sh.wikipedia.org',
            'zh-cn':'zh.wikipedia.org',
            'zh-tw':'zh.wikipedia.org'
            }
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikipedia.org'

        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': u'Wikipedia',
        }
        self.namespaces[5] = {
            '_default': u'Wikipedia talk',
            'af': u'WikipediaBespreking',
            'de': u'Wikipedia Diskussion',
            'pt': u'Wikipedia_Discussão',
            'es': u'Wikipedia Discusión',
        }
            
        # On most Wikipedias page names must start with a capital letter, but some
        # languages don't use this.
            
        self.nocapitalize = ['tlh','tokipona']
            
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.
            
        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'fr': self.alphabetic,
            'he': ['en'],
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic,
            'fi': self.alphabetic,
            'nn': ['no','nb','sv','da']
            }

        self.interwiki_putfirst_doubled = ['nn']

        self.obsolete = {'sh':'hr',
                    'dk':'da',
                    'minnan':'zh-min-nan',
                    'nb':'no',
                    'jp':'ja',
                    'tokipona':'none',
                    'zh-tw':'zh',
                    'zh-cn':'zh'}
            
        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wikimedia family./ca
        
        self.biglangs = ['de', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'pt', 'sv']
        
        self.biglangs2 = self.biglangs + [
            'ca', 'da', 'eo', 'et', 'fi', 'no', 'ro', 'sl', 'zh']
        
        self.biglangs3 = self.biglangs2 + [
            'af', 'bg', 'cs', 'he', 'hr', 'hu', 'id', 'la', 'ms', 'ru', 'uk', 'wa']
        
        self.biglangs4 = self.biglangs3 + [
            'ast', 'bs', 'cy', 'el', 'eu', 'fy', 'gl', 'ia', 'io', 'is',
            'ko', 'ku', 'lb', 'lt', 'nn', 'simple', 'sk', 'sr', 'tr', 'tt']
        
        self.seriouslangs = self.biglangs4 + [
            'als', 'an', 'ang', 'ar', 'be', 'csb', 'fa', 'fo', 'ga', 'gd',
            'hi', 'ie', 'jv', 'kn', 'ks', 'kw', 'lv', 'mi', 'minnan', 'ml', 'nds',
            'oc', 'sa', 'scn', 'sq', 'su', 'ta', 'th', 'tl', 'ur', 'vi']
        
        # other groups of language that we might want to do at once
            
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
        
        # Languages that are coded in iso-8859-1
        self.latin1 = ['en', 'sv', 'nl', 'da', 'dk']
        
        # Languages that used to be coded in iso-8859-1
        self.latin1old = ['de', 'et', 'es', 'ia', 'la', 'af', 'cs', 'fr', 'pt', 'sl', 'bs', 'fy',
                    'vi', 'lt', 'fi', 'it', 'no', 'simple', 'gl', 'eu',
                    'nds', 'co', 'mi', 'mr', 'id', 'lv', 'sw', 'tt', 'uk', 'vo',
                    'ga', 'na', 'es', 'test']
        
    def code2encoding(self, code):
        """Return the encoding for a specific language wikipedia"""
        if code in self.latin1:
            return 'iso-8859-1'
        return 'utf-8'
    
    def code2encodings(self, code):
        """Return a list of historical encodings for a specific language
           wikipedia"""
        # Historic compatibility
        if code == 'pl':
            return 'utf-8', 'iso-8859-2'
        if code == 'ru':
            return 'utf-8', 'iso-8859-5'
        if code in self.latin1old:
            return 'utf-8', 'iso-8859-1'
        return self.code2encoding(code),
