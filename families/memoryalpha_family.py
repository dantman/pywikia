# -*- coding: utf-8  -*-
import family, config
    
# The Memory Alpha family, a set of StarTrek wikis.

# A language not mentioned here is not known by the robot

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'memoryalpha'
    
        self.langs = {
            'de':'de',
            'en':'en',
            'nl':'nl',
            'sv':'sv',
            }
    
        # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
            '_default': u'Memory Alpha',
        }
        self.namespaces[5] = {
            '_default': u'Memory Alpha talk',
            'de': u'Memory Alpha Diskussion',
        }
        
        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wikimedia family.
    
        self.biglangs = ['en','de']

    def hostname(self,code):
        return 'www.memory-alpha.org'

    def path(self, code):
        return '/%s/index.php' % code

    def version(self, code):
        return "1.4"
