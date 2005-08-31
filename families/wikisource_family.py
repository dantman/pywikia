# -*- coding: utf-8  -*-
import urllib
import family, config

# The wikimedia family that is known as Wikisource

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikisource'
       
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikisource.org'
  
        # Most namespaces are inherited from family.Family()
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.

        self.namespaces[4] = {
            '_default': u'Wikisource',
        }
        self.namespaces[5] = {
            '_default': u'Wikisource talk',
        }
        
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.

        alphabetic = ['ar','da','de','el','en','fr','gl','he','it','la','nl','pl','pt','ro','ru']
            
#        self.interwiki_putfirst = {
#            'en': alphabetic,
#            'fr': alphabetic,
#            }
            
#        # group of languages that we might want to do at once
#            
#        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
