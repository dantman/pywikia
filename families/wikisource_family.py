# -*- coding: utf-8  -*-
import urllib
import family, config

__version__ = '$Id$'

# The wikimedia family that is known as Wikisource

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikisource'
       
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikisource.org'
  
        self.namespaces[4] = {
            '_default': [u'Wikisource', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Wikisource talk', self.namespaces[5]['_default']],
        }
        
        alphabetic = ['ar','da','de','el','en','es','fr','gl',
                      'he','hr','it','ja', 'ko','la','nl','pl',
                      'pt','ro','ru','sr','sv','zh']
        
        self.cyrilliclangs = ['ru', 'sr']
