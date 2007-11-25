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
        self.languages_by_size = [
                     'en','de','pl','it','sk','ru','pt','bs','bg','sl',
                     'es','tr','he','zh','id','sv','lt','ja','no','hu',
                     'el','fa','nl','cs','ku','fi','fr','ar','eo','ca',
                     'gl','ro','ka','hr','la','uk','da','et','sr','vi',
                     'sq','ko','eu','th','simple','nn','ast','ang','hi','lb',
                     'is','ta','az','mr','kn','am','co','ml','cy','wo',
                     'za','te','kr','qu','uz','tt','ur','af','vo','bm',
                     'cr','na','nds','ky','su','als','be','ug','gu','zh-min-nan',
                     'hy','ga','kk','ks','kw','tk',]
        
        for lang in self.languages_by_size:            
            self.langs[lang] = lang+'.wikiquote.org'

        self.obsolete = {'nb':'no',
                    'minnan':'zh-min-nan',
                    'zh-tw':'zh',
                    'zh-cn':'zh'}
    
        # Most namespaces are inherited from family.Family()
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.

        # Override defaults
        self.namespaces[2]['pl'] = u'Użytkownik'
        self.namespaces[3]['pl'] = u'Dyskusja użytkownika'

        self.namespaces[4] = {
            '_default': [u'Wikiquote', self.namespaces[4]['_default']],
            'ar': u'ويكي الاقتباس',
            'bg': u'Уикицитат',
            'bs': u'Wikicitati',
            'ca': u'Viquidites',
            'cs': u'Wikicitáty',
            'el': u'Βικιφθέγματα',
            'eo': u'Vikicitaro',
            'fa': u'ویکی‌گفتاورد',
            'fi': u'Wikisitaatit',
            'ga': u'Vicísliocht',
            'he': u'ויקיציטוט',
            'hr': u'Wikicitat',
            'hu': u'Wikidézet',
            'is': u'Wikivitnun',
            'ka': u'ვიკიციტატა',
            'kk': u'Уикидәйек',
            'la': u'Vicicitatio',
            'ml': u'വിക്കി ചൊല്ലുകള്‍',
            'pl': u'Wikicytaty',
            'ro': u'Wikicitat',
            'ru': u'Викицитатник',
            'sk': u'Wikicitáty',
            'sl': u'Wikinavedek',
            'tr': u'Vikisöz',
            'ur': u'وکی اقتباسات',
            'uz': u'Vikiiqtibos',
        }

        self.namespaces[5] = {
            '_default': [u'Wikiquote talk', self.namespaces[5]['_default']],
            'af': u'Wikiquotebespreking',
            'als': u'Wikiquote Diskussion',
            'ar': u'نقاش ويكي الاقتباس',
            'ast': u'Wikiquote discusión',
            'az': u'Wikiquote müzakirəsi',
            'be': u'Wikiquote размовы',
            'bg': u'Уикицитат беседа',
            'bm': u'Discussion Wikiquote',
            'br': u'Kaozeadenn Wikiquote',
            'bs': u'Razgovor s Wikicitatima',
            'ca': u'Viquidites Discussió',
            'cs': u'Wikicitáty diskuse',
            'cy': u'Sgwrs Wikiquote',
            'da': u'Wikiquote-diskussion',
            'de': u'Wikiquote Diskussion',
            'el': u'Βικιφθέγματα συζήτηση',
            'eo': u'Vikicitaro diskuto',
            'es': u'Wikiquote Discusión',
            'et': u'Wikiquote arutelu',
            'eu': u'Wikiquote eztabaida',
            'fa': u'بحث ویکی‌گفتاورد',
            'fi': u'Keskustelu Wikisitaatitista',
            'fr': u'Discussion Wikiquote',
            'ga': u'Plé Vicísliocht',
            'he': u'שיחת ויקיציטוט',
            'hi': u'Wikiquote वार्ता',
            'hr': u'Razgovor Wikicitat',
            'hu': u'Wikidézet vita',
            'hy': u'Wikiquote քննարկում',
            'id': u'Pembicaraan Wikiquote',
            'is': u'Wikivitnunspjall',
            'it': u'Discussioni Wikiquote',
            'ja': u'Wikiquote‐ノート',
            'ka': u'ვიკიციტატა განხილვა',
            'kk': u'Уикидәйек талқылауы',
            'kn': u'Wikiquote ಚರ್ಚೆ',
            'ko': u'Wikiquote토론',
            'ku': u'Wikiquote nîqaş',
            'la': u'Disputatio Vicicitationis',
            'lb': u'Wikiquote Diskussion',
            'li': u'Euverlèk Wikiquote',
            'lt': u'Wikiquote aptarimas',
            'ml': u'വിക്കി ചൊല്ലുകള്‍ സംവാദം',
            'mr': u'Wikiquote चर्चा',
            'nds': u'Wikiquote Diskuschoon',
            'nl': u'Overleg Wikiquote',
            'nn': u'Wikiquote-diskusjon',
            'no': u'Wikiquote-diskusjon',
            'pl': u'Dyskusja Wikicytatów',
            'pt': u'Wikiquote Discussão',
            'qu': u'Wikiquote rimanakuy',
            'ro': u'Discuţie Wikicitat',
            'ru': u'Обсуждение Викицитатника',
            'sk': u'Diskusia k Wikicitátom',
            'sl': u'Pogovor o Wikinavedku',
            'sq': u'Wikiquote diskutim',
            'sr': u'Разговор о Wikiquote',
            'su': u'Obrolan Wikiquote',
            'sv': u'Wikiquotediskussion',
            'ta': u'Wikiquote பேச்சு',
            'te': u'Wikiquote చర్చ',
            'th': u'คุยเรื่องWikiquote',
            'tr': u'Vikisöz tartışma',
            'tt': u'Wikiquote bäxäse',
            'uk': u'Обговорення Wikiquote',
            'ur': u'تبادلۂ خیال وکی اقتباسات',
            'uz': u'Vikiiqtibos munozarasi',
            'vi': u'Thảo luận Wikiquote',
            'vo': u'Bespik dö Wikiquote',
            'wo': u'Discussion Wikiquote',
        }
        
        self.namespaces[100] = {
            '_default': u'Portal',
            'he':       u'פורטל',
            'fr':       u'Portail',
            }
        
        self.namespaces[101] = {
            '_default': u'Portal talk',
            'de':       u'Portal Diskussion',
            'he':       u'שיחת פורטל',
            'fr':       u'Discussion Portail',
            }

        self.namespaces[102] = {
            'fr':       u'Projet',
            }

        self.namespaces[103] = {
            'fr':       u'Discussion Projet',
            }

        self.namespaces[104] = {
            'fr':       u'Référence',
            }

        self.namespaces[105] = {
            'fr':       u'Discussion Référence',
            }

        self.namespaces[108] = {
            '_default': u'Transwiki'
            }

        self.namespaces[109] = {
            '_default': u'Transwiki talk',
            'fr':       u'Discussion Transwiki'
            }
         
        self.disambiguationTemplates = {
            '_default': [u''],
            'ka':       [u'მრავალმნიშვნელოვანი', u'მრავმნიშ'],
            'pt':       [u'Desambiguação'],
            }

        # attop is a list of languages that prefer to have the interwiki
        # links at the top of the page.
        self.interwiki_attop = ['pl']

        # on_one_line is a list of languages that want the interwiki links
        # one-after-another on a single line
        self.interwiki_on_one_line = ['pl']
        
        # Similar for category
        self.category_attop = ['pl']

        # List of languages that want the category on_one_line.
        self.category_on_one_line = []
        
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
                    'fi','sv','ta','tt','th','ur','vi','tokipona',
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

        self.mainpages = {
            'ka':   u'მთავარი გვერდი'
        }

    def version(self, code):
        return "1.11alpha"    

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
    def shared_image_repository(self, code):
        return ('commons', 'commons')
