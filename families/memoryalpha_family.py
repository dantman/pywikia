# -*- coding: utf-8  -*-
import family
    
# The Memory Alpha family, a set of StarTrek wikis.

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'memoryalpha'
    
        self.langs = {
            'de': None,
            'en': None,
            'nl': None,
            'sv': None,
            }
    
        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': u'Memory Alpha',
        }
        self.namespaces[5] = {
            '_default': u'Memory Alpha talk',
            'de': u'Memory Alpha Diskussion',
            'nl': u'Overleg Memory Alpha',
            'sv': u'Memory Alphadiskussion',
        }
        
        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wiki family.
        self.biglangs = ['en', 'de']

    def hostname(self,code):
        return 'www.memory-alpha.org'

    def path(self, code):
        return '/%s/index.php' % code

    def version(self, code):
        return "1.4"
