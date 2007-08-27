# -*- coding: utf-8  -*-
import urllib
import family, config

__version__ = '$Id$'

# The wikimedia family that is known as Wikibooks

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikibooks'
        # Known wikibooks languages, given as a dictionary mapping the language code
        # to the hostname of the site hosting that wiktibooks. For human consumption,
        # the full name of the language is given behind each line as a comment
        self.langs = {
            'minnan':'zh-min-nan.wikibooks.org',
            'nb':'no.wikibooks.org',
            'zh-cn':'zh.wikibooks.org',
            'zh-tw':'zh.wikibooks.org'
            }
        
        for lang in self.knownlanguages:
            self.langs[lang] = '%s.wikibooks.org' % lang

        self.obsolete = {'nb':'no',
                    'minnan':'zh-min-nan',
                    'zh-tw':'zh',
                    'zh-cn':'zh'}

        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': [u'Wikibooks', self.namespaces[4]['_default']],
            'cs': u'Wikiknihy',
        }

        self.namespaces[5] = {
            '_default': [u'Wikibooks talk', self.namespaces[5]['_default']],
            'cs': u'Wikiknihy diskuse',
            'it': u'Discussioni Wikibooks',
            'pt': u'Wikibooks Discussão',
        }

        self.namespaces[100] = {
            '_default': u'Portal',
            'it': u'Portale',
        }
        
        self.namespaces[101] = {
            '_default': u'Portal talk',
            'it': u'Discussioni portale',
        }

        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.

        alphabetic = ['af','ar','roa-rup','om','bg','be','bn','bs',
                      'ca','chr','co','cs','cy','da','de','als','et',
                      'el','en','es','eo','eu','fa','fr','fy','ga','gv',
                      'gd','gl','ko','hi','hr','io','id','ia','is','it',
                      'he','jv','ka','csb','ks','sw','la','lv','lt','hu',
                      'mk','mg','ml','mi','mr','ms','zh-cfr','mn','nah','na',
                      'nl','ja','no','nb','oc','nds','pl','pt','ro','ru',
                      'sa','st','sq','si','simple','sk','sl','sr','su',
                      'fi','sv','ta','tt','th','ur','vi','tokipona',
                      'tpi','tr','uk','vo','yi','yo','za','zh','zh-cn',
                      'zh-tw']

        self.interwiki_putfirst = {
            'en': alphabetic,
            'fi': alphabetic,
            'fr': alphabetic,
            'hu': ['en'],
            'pl': alphabetic,
            'simple': alphabetic
        }

    def version(self, code):
        return "1.11"
    
    def shared_image_repository(self, code):
        return ('commons', 'commons')
