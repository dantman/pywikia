# -*- coding: utf-8  -*-
import family

# The Anarchopedia family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'anarchopedia'

        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.anarchopedia.org'

        self.namespaces[4] = {
            '_default': [u'Anarchopedia'],
        }
        self.namespaces[5] = {
            '_default': [u'Anarchopedia talk'],
        }
        
        self.nocapitalize = self.langs.keys()    
        
        alphabetic = ['ar','id','da', 'de', 'es', 'eo', 'fr', 'hr', 'it',
                      'nl', 'no', 'nn', 'pl', 'pt', 'en', 'ru', 'sr', 'sv']
            
    def version(self, code):
        return "1.6.8"

    def path(self, code):
        return '/index.php'
