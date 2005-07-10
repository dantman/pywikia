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
            'zh-cn':'zh.wikipedia.org',
            'zh-tw':'zh.wikipedia.org'
            }
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikipedia.org'

        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': u'Wikipedia',
            'ar': u'ويكيبيديا',
            'bg': u'Уикипедия',
            'ca': u'Viquipèdia',
            'cy': u'Wicipedia',
            'el': u'Βικιπαίδεια',
            'eo': u'Vikipedio',
            'he': u'ויקיפדיה',
            'fr': u'Wikipédia',
            'hu': u'Wikipédia',
            'ko': u'위키백과',
            'ru': u'Википедия',
            'sl': u'Wikipedija',
            'sk': u'Wikipédia',
            'sr': u'Википедија',
            'th': u'วกพเดย',# doesn't seem to be correct for some reason
        }
        self.namespaces[5] = {
            '_default': u'Wikipedia talk',
            'af': u'WikipediaBespreking',
            'de': u'Wikipedia Diskussion',
            'es': u'Wikipedia Discusión',
            'pt': u'Wikipedia_Discussão',
            'sl': u'Pogovor k Wikipediji',
        }
            
        # On most Wikipedias page names must start with a capital letter, but some
        # languages don't use this.
            
        self.nocapitalize = ['tlh','tokipona']
            
        # attop is a list of languages that prefer to have the interwiki
        # links at the top of the page.
        self.interwiki_attop = ['fr']
        # on_one_line is a list of languages that want the interwiki links
        # one-after-another on a single line
        self.interwiki_on_one_line = ['fr', 'hu']
        
        # Similar for category
        self.category_attop = ['fr']
        
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.
            
        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'et': self.alphabetic,
            'fr': self.alphabetic,
            'he': ['en'],
            'hu': ['en'],
            'lb': self.alphabetic,
            'pl': self.alphabetic,
            'simple': self.alphabetic,
            'fi': self.alphabetic,
            'nn': self.alphabetic
            }

        self.interwiki_putfirst_doubled = {
            'nn': [7, ['no','nb','sv','da']]
            }

        self.obsolete = {'dk':'da',
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
        
        self.biglangs = [
            'de', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'pt', 'sv']
        
        self.biglangs2 = self.biglangs + [
            'ca', 'da', 'eo', 'et', 'fi', 'hu', 'no', 'ro', 'sl', 'zh']
        
        self.biglangs3 = self.biglangs2 + [
            'bg', 'cs', 'gl', 'he', 'hr', 'id', 'ru', 'nn', 'sk', 'uk']
        
        self.biglangs4 = self.biglangs3 + [
            'af', 'ast', 'bs', 'cy', 'el', 'eu', 'ia', 'io', 'is', 'ko',
            'la', 'lb', 'lt', 'ms', 'nds', 'simple', 'sr', 'tr', 'tt', 'wa']

        self.biglangs5 = self.biglangs4 + [
             'als', 'an', 'ang', 'ar', 'be', 'bn', 'br', 'co', 'csb', 'fa',
             'fo', 'fy', 'ga', 'gd', 'gu', 'hi', 'hy', 'ie', 'jv', 'ka',
             'kn', 'ks', 'ku', 'kw', 'li', 'lv', 'mi', 'mk', 'ml', 'mr',
             'mt', 'nah', 'oc', 'os', 'sa', 'scn', 'se', 'sh', 'sq', 'su',
             'ta', 'te', 'th', 'tl', 'tpi', 'ur', 'vi', 'yi', 'zh-min-nan']

        self.seriouslangs = self.biglangs5

        # other groups of language that we might want to do at once
            
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
        
        # Languages that used to be coded in iso-8859-1
        self.latin1old = ['de', 'en', 'et', 'es', 'ia', 'la', 'af', 'cs',
                    'fr', 'pt', 'sl', 'bs', 'fy', 'vi', 'lt', 'fi', 'it',
                    'no', 'simple', 'gl', 'eu', 'nds', 'co', 'mi', 'mr',
                    'id', 'lv', 'sw', 'tt', 'uk', 'vo', 'ga', 'na', 'es',
                    'nl', 'da', 'dk', 'sv', 'test']
    
    def code2encodings(self, code):
        """Return a list of historical encodings for a specific language
           wikipedia"""
        # Historic compatibility
        if code == 'pl':
            return 'utf-8', 'iso8859-2'
        if code == 'ru':
            return 'utf-8', 'iso8859-5'
        if code in self.latin1old:
            return 'utf-8', 'iso-8859-1'
        return self.code2encoding(code),
