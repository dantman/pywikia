# -*- coding: utf-8  -*-
import urllib
import family, config

# The wikimedia family that is known as Wikiquote

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikiquote'
        
        self.langs = {
            'minnan':'zh-min-nan.wikiquote.org',
            'nb':'no.wikiquote.org',
            'zh-cn':'zh.wikiquote.org',
            'zh-tw':'zh.wikiquote.org'
            }
        
        for lang in self.knownlanguages:
            self.langs[lang] = lang+'.wikiquote.org'

        self.obsolete = {'nb':'no',
                    'minnan':'zh-min-nan',
                    'zh-tw':'zh',
                    'zh-cn':'zh'}
    
        # Most namespaces are inherited from family.Family()
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': u'Wikiquote',
        },
        self.namespaces[5] = {
            '_default': u'Wikiquote talk',
            'pt': u'Wikiquote DiscussÃ£o',
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
                    'fi','sv','ta','tt','th','tlh','ur','vi','tokipona',
                    'tpi','tr','uk','vo','yi','yo','za','zh','zh-cn',
                    'zh-tw']
            
        self.interwiki_putfirst = {
            'en': alphabetic,
            'fi': alphabetic,
            'fr': alphabetic,
            'he': ['en'],
            'hu': ['en'],
            'pl': alphabetic,
            'simple': alphabetic
            }
            
        # group of languages that we might want to do at once
            
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
