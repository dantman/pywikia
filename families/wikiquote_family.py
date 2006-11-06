# -*- coding: utf-8  -*-
import urllib
import family, config

__version__ = '$Id$'

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
            '_default': [u'Wikiquote', self.namespaces[4]['_default']],
            'ar':       u'ويكي الاقتباس',
            'bg':       u'Уикицитат',
            'bs':       u'Wikicitati',
            'eo':       u'Vikicitaro',
            'fa':       u'ویکی‌گفتاورد',
            'fi':       u'Wikisitaatit',
            'he':       u'ויקיציטוט',
            'hu':       u'Wikidézet',
            'hr':       u'Wikicitat',
            'ka':       u'ვიკიციტატა',
            'la':       u'Vicicitatio',
            'pl':       u'Wikicytaty',
            'ro':       u'Wikicitat',
            'ru':       u'Викицитатник',
            'sl':       u'Wikinavedek',
            'sk':       u'Wikicitáty',
            'tr':       u'Vikisöz',
            
        }
        self.namespaces[5] = {
            '_default': [u'Wikiquote talk', self.namespaces[5]['_default']],
            'ar':       u'نقاش ويكي الاقتباس',
            'bg':       u'Уикицитат беседа',
            'bs':       u'Razgovor s Wikicitatima',
            'ca':       u'Wikiquote Discussió',
            'cs':       u'Wikiquote diskuse',
            'da':       u'Wikiquote-diskussion',
            'de':       u'Wikiquote Diskussion',
            'eo':       u'Vikicitaro diskuto',
            'el':       u'Wikiquote συζήτηση',
            'es':       u'Wikiquote Discusión',
            'et':       u'Wikiquote arutelu',
            'eu':       u'Wikiquote eztabaida',
            'fa':       u'بحث ویکی‌گفتاورد',
            'fi':       u'Keskustelu Wikisitaateista',
            'fr':       u'Discussion Wikiquote',
            'he':       u'שיחת ויקיציטוט',
            'hr':       u'Razgovor Wikicitat',
            'hu':       u'Wikidézet vita',
            'it':       u'Discussioni Wikiquote',
            'ja':       u'Wikiquote‐ノート',
            'ka':       u'ვიკიციტატა განხილვა',
            'ko':       u'Wikiquote토론',
            'ku':       u'Wikiquote nîqaş',
            'la':       u'Disputatio Vicicitationis',
            'lt':       u'Wikiquote aptarimas',
            'nl':       u'Overleg Wikiquote',
            'no':       u'Wikiquote-diskusjon',
            'pl':       u'Dyskusja Wikicytatów',
            'pt':       u'Wikiquote Discussão',
            'ro':       u'Discuţie Wikicitat',
            'ru':       u'Обсуждение Викицитатника',
            'sk':       u'Diskusia k Wikicitátom',
            'sl':       u'Pogovor o Wikinavedku',
            'sr':       u'Разговор о Wikiquote',
            'sv':       u'Wikiquotediskussion',
            'tr':       u'Vikisöz tartışma',
            'uk':       u'Обговорення Wikiquote',
        }
        
        self.namespaces[100] = {
            '_default': u'Portal',
            'he':       u'פורטל',
        }
        
        self.namespaces[101] = {
            '_default': u'Portal talk',
            'he':       u'שיחת פורטל',
        }
        

        self.disambiguationTemplates = {
            '_default': [u''],
            'ka':       [u'მრავალმნიშვნელოვანი', u'მრავმნიშ'],
            'pt':       [u'Desambiguação'],
        }

        # attop is a list of languages that prefer to have the interwiki
        # links at the top of the page.
        self.interwiki_attop = ['fr', 'pl']

        # on_one_line is a list of languages that want the interwiki links
        # one-after-another on a single line
        self.interwiki_on_one_line = ['fr', 'pl']
        
        # Similar for category
        self.category_attop = ['pl']

        # List of languages that want the category on_one_line.
        self.category_on_one_line = ['fr']
        
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
                    'he','jv','ka','csb','ks','sw','la','lt','hu',
                    'mk','mg','ml','mi','mr','zh-cfr','mn','nah','na',
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
            'simple': alphabetic,
            'pt': alphabetic,
            }
            
        # group of languages that we might want to do at once
            
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic

        self.mainpages = {
            'ka':   u'მთავარი გვერდი'
            }

    def version(self, code):
        return "1.8alpha"    

    def code2encodings(self, code):
        """
        Return a list of historical encodings for a specific language wikipedia
        """
        # Historic compatibility
        if code == 'pl':
            return 'utf-8', 'iso8859-2'
        if code == 'ru':
            return 'utf-8', 'iso8859-5'
        return self.code2encoding(code),
