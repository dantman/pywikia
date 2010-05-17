# -*- coding: utf-8  -*-
import family

__version__ = '$Id$'

# The Wikimedia family that is known as Wikisource

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikisource'

        self.languages_by_size = [
            'en', 'zh', 'ru', 'pt', 'fr', 'de', 'es', 'it', 'he', 'ar', 'hu',
            'fa', 'pl', 'th', 'cs', 'ro', 'hr', 'te', 'fi', 'tr', 'nl', 'sv',
            'sl', 'uk', 'ko', 'vi', 'bn', 'sr', 'ja', 'el', 'la', 'li', 'yi',
            'ml', 'az', 'is', 'bs', 'hy', 'ca', 'id', 'mk', 'no', 'da', 'ta',
            'et', 'bg', 'lt', 'gl', 'kn', 'cy', 'sk', 'zh-min-nan', 'fo',
        ]

        if family.config.SSL_connection:
            for lang in self.languages_by_size:
                self.langs[lang] = None
            self.langs['-'] = None
        else:
            for lang in self.languages_by_size:
                self.langs[lang] = '%s.wikisource.org' % lang
            self.langs['-'] = 'wikisource.org'

        # Override defaults
        self.namespaces[2]['pl'] = 'Wikiskryba'
        self.namespaces[3]['pl'] = 'Dyskusja wikiskryby'

        # Most namespaces are inherited from family.Family.
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': [u'Wikisource', self.namespaces[4]['_default']],
            'ang': u'Wicifruma',
            'ar': u'ويكي مصدر',
            'az': u'VikiMənbə',
            'bg': u'Уикиизточник',
            'bn': u'উইকিসংকলন',
            'bs': u'Wikizvor',
            'ca': u'Viquitexts',
            'cs': u'Wikizdroje',
            'cy': u'Wicitestun',
            'el': u'Βικιθήκη',
            'et': u'Vikitekstid',
            'fa': u'ویکی‌نبشته',
            'fi': u'Wikiaineisto',
            'fo': u'Wikiheimild',
            'he': u'ויקיטקסט',
            'hr': u'Wikizvor',
            'ht': u'Wikisòrs',
            'hu': u'Wikiforrás',
            'hy': u'Վիքիդարան',
            'is': u'Wikiheimild',
            'ko': u'위키문헌',
            'la': u'Vicifons',
            'li': u'Wikibrónne',
            'lt': u'Vikišaltiniai',
            'ml': u'വിക്കിഗ്രന്ഥശാല',
            'nb': u'Wikikilden',
            'no': u'Wikikilden',
            'pl': u'Wikiźródła',
            'ru': u'Викитека',
            'sl': u'Wikivir',
            'sr': u'Викизворник',
            'th': u'วิกิซอร์ซ',
            'tr': u'VikiKaynak',
            'yi': [u'װיקיביבליאָטעק', u'וויקיביבליאטעק'],
            'zh': [u'Wikisource', u'维基文库'],
        }
        self.namespaces[5] = {
            '_default': [u'Wikisource talk', self.namespaces[5]['_default']],
            'ang': u'Wicifruma talk',
            'ar': u'نقاش ويكي مصدر',
            'az': u'VikiMənbə müzakirəsi',
            'bg': u'Уикиизточник беседа',
            'bn': u'উইকিসংকলন আলোচনা',
            'bs': u'Razgovor s Wikizvor',
            'ca': u'Viquitexts Discussió',
            'cs': u'Diskuse k Wikizdrojům',
            'cy': u'Sgwrs Wicitestun',
            'da': u'Wikisource-diskussion',
            'de': u'Wikisource Diskussion',
            'el': u'Βικιθήκη συζήτηση',
            'es': u'Wikisource Discusión',
            'et': u'Vikitekstide arutelu',
            'fa': u'بحث ویکی‌نبشته',
            'fi': u'Keskustelu Wikiaineistosta',
            'fo': u'Wikiheimild-kjak',
            'fr': u'Discussion Wikisource',
            'gl': u'Conversa Wikisource',
            'he': u'שיחת ויקיטקסט',
            'hr': u'Razgovor o Wikizvoru',
            'ht': u'Diskisyon Wikisòrs',
            'hu': u'Wikiforrás-vita',
            'hy': u'Վիքիդարանի քննարկում',
            'id': u'Pembicaraan Wikisource',
            'is': u'Wikiheimildspjall',
            'it': u'Discussioni Wikisource',
            'ja': u'Wikisource・トーク',
            'kn': u'Wikisource ಚರ್ಚೆ',
            'ko': u'위키문헌토론',
            'la': u'Disputatio Vicifontis',
            'li': u'Euverlèk Wikibrónne',
            'lt': u'Vikišaltiniai aptarimas',
            'mk': u'Разговор за Wikisource',
            'ml': u'വിക്കിഗ്രന്ഥശാല സംവാദം',
            'nb': u'Wikikilden-diskusjon',
            'nl': u'Overleg Wikisource',
            'no': u'Wikikilden-diskusjon',
            'pl': u'Dyskusja Wikiźródeł',
            'pt': u'Wikisource Discussão',
            'ro': u'Discuţie Wikisource',
            'ru': u'Обсуждение Викитеки',
            'sk': u'Diskusia k Wikisource',
            'sl': u'Pogovor o Wikiviru',
            'sr': u'Разговор о Викизворнику',
            'sv': u'Wikisourcediskussion',
            'ta': u'Wikisource பேச்சு',
            'te': u'Wikisource చర్చ',
            'th': u'คุยเรื่องวิกิซอร์ซ',
            'tr': u'VikiKaynak tartışma',
            'uk': u'Обговорення Wikisource',
            'vi': u'Thảo luận Wikisource',
            'yi': [u'װיקיביבליאָטעק רעדן', u'וויקיביבליאטעק רעדן'],
            'zh': [u'Wikisource talk', u'维基文库讨论'],
        }
        self.namespaces[100] = {
            'ar': u'بوابة',
            'bg': u'Автор',
            'bn': u'লেখক',
            'cs': u'Autor',
            'el': u'Σελίδα',
            'en': u'Portal',
            'fa': [u'درگاه', u'Portal'],
            'fr': u'Transwiki',
            'he': u'קטע',
            'hr': u'Autor',
            'hu': u'Szerző',
            'hy': u'Հեղինակ',
            'nl': u'Hoofdportaal',
            'pl': u'Strona',
            'pt': u'Portal',
            'sl': u'Stran',
            'te': u'ద్వారము',
            'tr': u'Kişi',
            'vi': u'Chủ đề',
        }
        self.namespaces[101] = {
            'ar': u'نقاش البوابة',
            'bg': u'Автор беседа',
            'bn': u'লেখক আলাপ',
            'cs': u'Diskuse k autorovi',
            'el': u'Συζήτηση σελίδας',
            'en': u'Portal talk',
            'fa': [u'بحث درگاه', u'Portal talk'],
            'fr': u'Discussion Transwiki',
            'he': u'שיחת קטע',
            'hr': u'Razgovor o autoru',
            'hu': u'Szerző vita',
            'hy': u'Հեղինակի քննարկում',
            'nl': u'Overleg hoofdportaal',
            'pl': u'Dyskusja strony',
            'pt': u'Portal Discussão',
            'sl': u'Pogovor o strani',
            'te': u'ద్వారము చర్చ',
            'tr': u'Kişi tartışma',
            'vi': u'Thảo luận Chủ đề',
        }
        self.namespaces[102] = {
            'ar': u'مؤلف',
            'ca': u'Pàgina',
            'da': [u'Forfatter', u'Author'],
            'de': u'Seite',
            'el': u'Βιβλίο',
            'en': u'Author',
            'es': u'Página',
            'et': u'Lehekülg',
            'fa': [u'مؤلف', u'Author'],
            'fr': u'Auteur',
            'hr': u'Stranica',
            'hy': u'Պորտալ',
            'it': u'Autore',
            'la': u'Scriptor',
            'nb': u'Forfatter',
            'no': u'Forfatter',
            'pl': u'Indeks',
            'pt': u'Autor',
            'te': u'రచయిత',
            'vi': u'Tác gia',
            'zh': u'Author',
        }
        self.namespaces[103] = {
            'ar': u'نقاش المؤلف',
            'ca': u'Pàgina Discussió',
            'da': [u'Forfatterdiskussion', u'Author talk'],
            'de': u'Seite Diskussion',
            'el': u'Συζήτηση βιβλίου',
            'en': u'Author talk',
            'es': u'Página Discusión',
            'et': u'Lehekülje arutelu',
            'fa': [u'بحث مؤلف', u'Author talk'],
            'fr': u'Discussion Auteur',
            'hr': u'Razgovor o stranici',
            'hy': u'Պորտալի քննարկում',
            'it': u'Discussioni autore',
            'la': u'Disputatio Scriptoris',
            'nb': u'Forfatterdiskusjon',
            'no': u'Forfatterdiskusjon',
            'pl': u'Dyskusja indeksu',
            'pt': u'Autor Discussão',
            'te': u'రచయిత చర్చ',
            'vi': u'Thảo luận Tác gia',
            'zh': u'Author talk',
        }

        self.namespaces[104] = {
            '-': u'Page',
            'ar': u'صفحة',
            'ca': u'Llibre',
            'de': u'Index',
            'en': u'Page',
            'es': u'Índice',
            'et': u'Register',
            'fa': [u'برگه', u'Page'],
            'fr': u'Page',
            'he': u'עמוד',
            'hr': u'Sadržaj',
            'hu': u'Oldal',
            'hy': u'Էջ',
            'it': u'Progetto',
            'la': u'Pagina',
            'no': u'Side',
            'pl': u'Autor',
            'pt': u'Galeria',
            'ru': u'Страница',
            'sl': u'Kazalo',
            'sv': u'Sida',
            'te': [u'పేజీ', u'Page'],
            'vi': u'Trang',
            'zh': u'Page',
        }

        self.namespaces[105] = {
            '-': u'Page talk',
            'ar': u'نقاش الصفحة',
            'ca': u'Llibre Discussió',
            'de': u'Index Diskussion',
            'en': u'Page talk',
            'es': u'Índice Discusión',
            'et': u'Registri arutelu',
            'fa': [u'بحث برگه', u'Page talk'],
            'fr': u'Discussion Page',
            'he': u'שיחת עמוד',
            'hr': u'Razgovor o sadržaju',
            'hu': u'Oldal vita',
            'hy': u'Էջի քննարկում',
            'it': u'Discussioni progetto',
            'la': u'Disputatio Paginae',
            'no': u'Sidediskusjon',
            'pl': u'Dyskusja autora',
            'pt': u'Galeria Discussão',
            'ru': u'Обсуждение страницы',
            'sl': u'Pogovor o kazalu',
            'sv': u'Siddiskussion',
            'te': [u'పేజీ చర్చ', u'Page talk'],
            'vi': u'Thảo luận Trang',
            'zh': u'Page talk',
        }

        self.namespaces[106] = {
            '-': u'Index',
            'ar': u'فهرس',
            'en': u'Index',
            'et': u'Autor',
            'fr': u'Portail',
            'he': u'ביאור',
            'hu': u'Index',
            'hy': u'Ինդեքս',
            'it': u'Portale',
            'la': u'Liber',
            'no': u'Indeks',
            'pt': u'Página',
            'ru': u'Индекс',
            'sv': u'Författare',
            'vi': u'Mục lục',
            'zh': u'Index',
        }

        self.namespaces[107] = {
            '-': u'Index talk',
            'ar': u'نقاش الفهرس',
            'en': u'Index talk',
            'et': u'Autori arutelu',
            'fr': u'Discussion Portail',
            'he': u'שיחת ביאור',
            'hu': u'Index vita',
            'hy': u'Ինդեքսի քննարկում',
            'it': u'Discussioni portale',
            'la': u'Disputatio Libri',
            'no': u'Indeksdiskusjon',
            'pt': u'Página Discussão',
            'ru': u'Обсуждение индекса',
            'sv': u'Författardiskussion',
            'vi': u'Thảo luận Mục lục',
            'zh': u'Index talk',
        }

        self.namespaces[108] = {
            'he': u'מחבר',
            'it': u'Pagina',
            'pt': u'Em Tradução',
            'sv': u'Index',
        }

        self.namespaces[109] = {
            'he': u'שיחת מחבר',
            'it': u'Discussioni pagina',
            'pt': u'Discussão Em Tradução',
            'sv': u'Indexdiskussion',
        }

        self.namespaces[110] = {
            'he': u'תרגום',
            'it': u'Indice',
            'pt': u'Anexo',
        }

        self.namespaces[111] = {
            'he': u'שיחת תרגום',
            'it': u'Discussioni indice',
            'pt': u'Anexo Discussão',
        }

        self.namespaces[112] = {
            'fr': u'Livre',
            'he': u'מפתח',
        }

        self.namespaces[113] = {
            'fr': u'Discussion Livre',
            'he': u'שיחת מפתח',
        }

        self.alphabetic = ['ang','ar','az','bg','bs','ca','cs','cy',
                      'da','de','el','en','es','et','fa','fi',
                      'fo','fr','gl','he','hr','ht','hu','id',
                      'is','it','ja', 'ko','la','lt','ml','nl',
                      'no','pl','pt','ro','ru','sk','sl','sr',
                      'sv','te','th','tr','uk','vi','yi','zh']

        self.obsolete = {
            'ang': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Old_English_Wikisource
            'dk': 'da',
            'ht': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Haitian_Creole_Wikisource
            'jp': 'ja',
            'minnan':'zh-min-nan',
            'nb': 'no',
            'tokipona': None,
            'zh-tw': 'zh',
            'zh-cn': 'zh'
        }

        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'fi': self.alphabetic,
            'fr': self.alphabetic,
            'he': ['en'],
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
        }
        # Global bot allowed languages on http://meta.wikimedia.org/wiki/Bot_policy/Implementation#Current_implementation
        self.cross_allowed = [
            'el','fa','it','ko','no','vi','zh'
        ]
        # CentralAuth cross avaliable projects.
        self.cross_projects = [
            'wikipedia', 'wiktionary', 'wikibooks', 'wikiquote', 'wikinews', 'wikiversity', 
            'meta', 'mediawiki', 'test', 'incubator', 'commons', 'species'
        ]

    def version(self, code):
        return '1.16wmf4'

    def shared_image_repository(self, code):
        return ('commons', 'commons')

    if family.config.SSL_connection:
        def hostname(self, code):
            return 'secure.wikimedia.org'

        def protocol(self, code):
            return 'https'

        def scriptpath(self, code):
            if code == '-':
                return '/wikipedia/sources/w'
            
            return '/%s/%s/w' % (self.name, code)

        def nicepath(self, code):
            if code == '-':
                return '/wikipedia/sources/wiki/'
            return '/%s/%s/wiki/' % (self.name, code)
