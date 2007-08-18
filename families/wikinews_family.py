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
        
        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': [u'Wikinews', self.namespaces[4]['_default']],
            'pt': u'Wikinotícias',
        }
        self.namespaces[5] = {
            '_default': [u'Wikinews talk', self.namespaces[5]['_default']],
            'pt': u'Wikinotícias_Discussão',
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
