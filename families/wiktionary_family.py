# -*- coding: utf-8  -*-
import family

__version__ = '$Id$'

# The Wikimedia family that is known as Wiktionary

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wiktionary'

        self.languages_by_size = [
            'fr', 'en', 'lt', 'tr', 'zh', 'ru', 'vi', 'io', 'pl', 'pt', 'fi',
            'hu', 'el', 'no', 'ta', 'de', 'sv', 'it', 'ko', 'nl', 'kn', 'lo',
            'ml', 'ja', 'ku', 'ar', 'es', 'ro', 'et', 'id', 'te', 'gl', 'bg',
            'uk', 'ca', 'li', 'vo', 'fa', 'is', 'scn', 'sr', 'af', 'cs', 'th',
            'simple', 'fy', 'sw', 'oc', 'br', 'he', 'hr', 'sl', 'hy', 'sq',
            'tt', 'la', 'zh-min-nan', 'da', 'wa', 'ne', 'tk', 'ast', 'ur',
            'hsb', 'mg', 'kk', 'ky', 'eo', 'lv', 'my', 'wo', 'ang', 'ka', 'co',
            'hi', 'ga', 'gn', 'az', 'ia', 'eu', 'sk', 'csb', 'ms', 'st', 'tl',
            'cy', 'mr', 'nds', 'kl', 'be', 'sd', 'ug', 'ps', 'ti', 'sh', 'mk',
            'an', 'bn', 'gu', 'km', 'ss', 'ts', 'qu', 'bs', 'fo', 'am', 'rw',
            'chr', 'su', 'om', 'mn', 'nah', 'ie', 'iu', 'yi', 'mt', 'gv', 'kw',
            'gd', 'si', 'tg', 'nn', 'zu', 'dv', 'tpi', 'pa', 'roa-rup', 'jv',
            'sg', 'uz', 'mi', 'ik', 'so', 'ha', 'ay', 'lb', 'sa', 'na', 'jbo',
            'tn', 'sm', 'ks', 'fj', 'ln', 'za', 'dz', 'als',
        ]

        if family.config.SSL_connection:
            self.langs = dict([(lang, None) for lang in self.languages_by_size])
        else:
            self.langs = dict([(lang, '%s.wiktionary.org' % lang) for lang in self.languages_by_size])

        # Override defaults
        self.namespaces[2]['eo'] = u'Uzanto'
        self.namespaces[3]['eo'] = u'Uzanta diskuto'
        self.namespaces[2]['pl'] = u'Wikipedysta'
        self.namespaces[3]['pl'] = u'Dyskusja Wikipedysty'

        # Most namespaces are inherited from family.Family.
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': [u'Wiktionary', self.namespaces[4]['_default']],
            'ar': u'ويكاموس',
            'ast': u'Uiccionariu',
            'bg': u'Уикиречник',
            'bn': u'উইকিঅভিধান',
            'br': u'Wikeriadur',
            'bs': u'Vikirječnik',
            'ca': u'Viccionari',
            'cs': u'Wikislovník',
            'cy': u'Wiciadur',
            'el': u'Βικιλεξικό',
            'eo': u'Vikivortaro',
            'es': u'Wikcionario',
            'et': u'Vikisõnastik',
            'fa': u'ویکی‌واژه',
            'fi': u'Wikisanakirja',
            'fo': u'Wiktionary',
            'fr': u'Wiktionnaire',
            'ga': u'Vicífhoclóir',
            'gu': u'વિક્ષનરી',
            'he': u'ויקימילון',
            'hi': u'विक्षनरी',
            'hr': u'Wječnik',
            'hu': u'Wikiszótár',
            'hy': u'Վիքիբառարան',
            'ia': u'Wiktionario',
            'io': u'Wikivortaro',
            'is': u'Wikiorðabók',
            'it': u'Wikizionario',
            'ka': u'ვიქსიკონი',
            'kk': u'Уикисөздік',
            'ko': u'위키낱말사전',
            'la': u'Victionarium',
            'lt': u'Vikižodynas',
            'ml': u'വിക്കിനിഘണ്ടു',
            'ms': u'Wiktionary',
            'mt': u'Wikizzjunarju',
            'nl': u'WikiWoordenboek',
            'oc': u'Wikiccionari',
            'pl': u'Wikisłownik',
            'ps': u'ويکيسيند',
            'pt': u'Wikcionário',
            'ro': u'Wikţionar',
            'ru': u'Викисловарь',
            'scn': u'Wikizziunariu',
            'sk': u'Wikislovník',
            'sl': u'Wikislovar',
            'sr': u'Викиречник',
            'tk': u'Wikisözlük',
            'tr': u'Vikisözlük',
            'tt': u'Wiktionary',
            'uk': u'Вікісловник',
            'ur': u'وکی لغت',
            'uz': u'Vikilug‘at',
            'vo': u'Vükivödabuk',
            'yi': [u'װיקיװערטערבוך', u'וויקיווערטערבוך'],
            'zh': [u'Wiktionary', u'维基词典'],
        }

        self.namespaces[5] = {
            '_default': [u'Wiktionary talk', self.namespaces[5]['_default']],
            'ab': u'Обсуждение Wiktionary',
            'af': u'Wiktionarybespreking',
            'als': u'Wiktionary Diskussion',
            'am': u'Wiktionary ውይይት',
            'an': u'Descusión Wiktionary',
            'ar': u'نقاش ويكاموس',
            'ast': u'Uiccionariu alderique',
            'av': u'Обсуждение Wiktionary',
            'ay': u'Wiktionary Discusión',
            'az': u'Wiktionary müzakirəsi',
            'ba': u'Wiktionary б-са фекер алышыу',
            'be': u'Wiktionary размовы',
            'bg': u'Уикиречник беседа',
            'bm': u'Discussion Wiktionary',
            'bn': u'উইকিঅভিধান আলোচনা',
            'br': u'Kaozeadenn Wikeriadur',
            'bs': u'Razgovor s Vikirječnikom',
            'ca': u'Viccionari Discussió',
            'cs': u'Diskuse k Wikislovníku',
            'csb': u'Diskùsëjô Wiktionary',
            'cy': u'Sgwrs Wiciadur',
            'da': u'Wiktionary-diskussion',
            'de': u'Wiktionary Diskussion',
            'el': u'Συζήτηση βικιλεξικού',
            'eo': u'Vikivortaro diskuto',
            'es': u'Wikcionario Discusión',
            'et': u'Vikisõnastiku arutelu',
            'eu': u'Wiktionary eztabaida',
            'fa': u'بحث ویکی‌واژه',
            'fi': u'Keskustelu Wikisanakirjasta',
            'fo': u'Wiktionary-kjak',
            'fr': u'Discussion Wiktionnaire',
            'fy': u'Wiktionary oerlis',
            'ga': u'Plé Vicífhoclóra',
            'gl': u'Conversa Wiktionary',
            'gn': u'Wiktionary myangekõi',
            'gu': u'વિક્ષનરી ચર્ચા',
            'gv': u'Resooney Wiktionary',
            'he': u'שיחת ויקימילון',
            'hi': u'विक्षनरी वार्ता',
            'hr': u'Razgovor Wječnik',
            'hsb': u'Wiktionary diskusija',
            'hu': u'Wikiszótár-vita',
            'hy': u'Վիքիբառարանի քննարկում',
            'ia': u'Discussion Wiktionario',
            'id': u'Pembicaraan Wiktionary',
            'io': u'Wikivortaro Debato',
            'is': [u'Wikiorðabókarspjall', u'Wikiorðabókspjall'],
            'it': u'Discussioni Wikizionario',
            'ja': u'Wiktionary・トーク',
            'jv': u'Dhiskusi Wiktionary',
            'ka': u'ვიქსიკონი განხილვა',
            'kk': u'Уикисөздік талқылауы',
            'kl': u'Wiktionary-p oqalliffia',
            'km': u'ការពិភាក្សាអំពីWiktionary',
            'kn': u'Wiktionary ಚರ್ಚೆ',
            'ko': u'위키낱말사전토론',
            'ku': u'Wiktionary nîqaş',
            'kw': u'Keskows Wiktionary',
            'la': u'Disputatio Victionarii',
            'lb': u'Wiktionary Diskussioun',
            'li': u'Euverlèk Wiktionary',
            'ln': u'Discussion Wiktionary',
            'lo': u'ສົນທະນາກ່ຽວກັບWiktionary',
            'lt': u'Vikižodyno aptarimas',
            'lv': u'Wiktionary diskusija',
            'mg': u'Dinika amin\'ny Wiktionary',
            'mk': u'Разговор за Wiktionary',
            'ml': u'വിക്കിനിഘണ്ടു സംവാദം',
            'mn': u'Wiktionary-н хэлэлцүүлэг',
            'mr': u'Wiktionary चर्चा',
            'ms': u'Perbincangan Wiktionary',
            'mt': u'Diskussjoni Wikizzjunarju',
            'nah': u'Wiktionary tēixnāmiquiliztli',
            'nap': [u'Wiktionary chiàcchiera', u'Discussioni Wiktionary'],
            'nds': u'Wiktionary Diskuschoon',
            'nl': u'Overleg WikiWoordenboek',
            'nn': u'Wiktionary-diskusjon',
            'no': u'Wiktionary-diskusjon',
            'oc': u'Discussion Wikiccionari',
            'pa': u'Wiktionary ਚਰਚਾ',
            'pl': u'Wikidyskusja',
            'ps': u'د ويکيسيند خبرې اترې',
            'pt': u'Wikcionário Discussão',
            'qu': u'Wiktionary rimanakuy',
            'ro': u'Discuție Wikţionar',
            'ru': u'Обсуждение Викисловаря',
            'sa': u'Wiktionaryसंभाषणं',
            'sc': u'Wiktionary discussioni',
            'scn': u'Discussioni Wikizziunariu',
            'sd': u'Wiktionary بحث',
            'sg': u'Discussion Wiktionary',
            'si': u'Wiktionary සාකච්ඡාව',
            'sk': u'Diskusia k Wikislovníku',
            'sl': u'Pogovor o Wikislovarju',
            'sq': u'Wiktionary diskutim',
            'sr': u'Разговор о викиречнику',
            'su': u'Obrolan Wiktionary',
            'sv': u'Wiktionarydiskussion',
            'sw': u'Majadiliano ya Wiktionary',
            'ta': u'Wiktionary பேச்சு',
            'te': u'Wiktionary చర్చ',
            'tg': u'Баҳси Wiktionary',
            'th': u'คุยเรื่องWiktionary',
            'tk': [u'Wikisözlük çekişme', u'Wikisözlük talk'],
            'tl': u'Usapang Wiktionary',
            'tr': u'Vikisözlük tartışma',
            'tt': [u'Wiktionary бәхәсе', u'Wiktionary bäxäse'],
            'uk': u'Обговорення Вікісловника',
            'ur': u'تبادلۂ خیال وکی لغت',
            'uz': u'Vikilug‘at munozarasi',
            'vi': u'Thảo luận Wiktionary',
            'vo': u'Bespik dö Vükivödabuk',
            'wa': u'Wiktionary copene',
            'wo': u'Wiktionary waxtaan',
            'yi': [u'װיקיװערטערבוך רעדן', u'וויקיווערטערבוך רעדן'],
            'za': u'Wiktionary讨论',
            'zh': [u'Wiktionary talk', u'维基词典讨论'],
        }

        self.namespaces[90] = {
            'en': u'Thread',
        }

        self.namespaces[91] = {
            'en': u'Thread talk',
        }

        self.namespaces[92] = {
            'en': u'Summary',
        }

        self.namespaces[93] = {
            'en': u'Summary talk',
        }

        self.namespaces[100] = {
            'bg': u'Словоформи',
            'bn': u'উইকিসরাস',
            'bs': u'Portal',
            'cy': u'Atodiad',
            'el': u'Παράρτημα',
            'en': u'Appendix',
            'es': u'Apéndice',
            'fa': u'پیوست',
            'fi': u'Liite',
            'fr': u'Annexe',
            'ga': u'Aguisín',
            'he': u'נספח',
            'it': u'Appendice',
            'ko': u'부록',
            'lt': u'Sąrašas',
            'no': u'Tillegg',
            'oc': u'Annèxa',
            'pl': u'Aneks',
            'pt': u'Apêndice',
            'ro': u'Portal',
            'ru': [u'Приложение', u'Appendix'],
            'sr': u'Портал',
            'tr': u'Portal',
            'uk': u'Додаток',
        }
        self.namespaces[101] = {
            'bg': u'Словоформи беседа',
            'bn': u'উইকিসরাস আলোচনা',
            'bs': u'Razgovor o Portalu',
            'cy': u'Sgwrs Atodiad',
            'el': u'Συζήτηση παραρτήματος',
            'en': u'Appendix talk',
            'es': u'Apéndice Discusión',
            'fa': u'بحث پیوست',
            'fi': u'Keskustelu liitteestä',
            'fr': u'Discussion Annexe',
            'ga': u'Plé aguisín',
            'he': u'שיחת נספח',
            'it': u'Discussioni appendice',
            'ko': u'부록 토론',
            'lt': u'Sąrašo aptarimas',
            'no': u'Tilleggdiskusjon',
            'oc': u'Discussion Annèxa',
            'pl': u'Dyskusja aneksu',
            'pt': u'Apêndice Discussão',
            'ro': u'Discuţie Portal',
            'ru': [u'Обсуждение приложения', u'Appendix talk'],
            'sr': u'Разговор о порталу',
            'tr': u'Portal tartışma',
            'uk': u'Обговорення додатка',
        }

        self.namespaces[102] = {
            'bs': u'Indeks',
            'cy': u'Odliadur',
            'de': u'Verzeichnis',
            'en': u'Concordance',
            'fr': u'Transwiki',
            'ia': u'Appendice',
            'pl': u'Indeks',
            'pt': u'Vocabulário',
            'ro': u'Apendice',
            'ru': [u'Конкорданс', u'Concordance'],
            'sv': u'Appendix',
            'uk': u'Індекс',
        }

        self.namespaces[103] = {
            'bs': u'Razgovor o Indeksu',
            'cy': u'Sgwrs Odliadur',
            'de': u'Verzeichnis Diskussion',
            'en': u'Concordance talk',
            'fr': u'Discussion Transwiki',
            'ia': u'Discussion Appendice',
            'pl': u'Dyskusja indeksu',
            'pt': u'Vocabulário Discussão',
            'ro': u'Discuţie Apendice',
            'ru': [u'Обсуждение конкорданса', u'Concordance talk'],
            'sv': u'Appendixdiskussion',
            'uk': u'Обговорення індексу',
        }

        self.namespaces[104] = {
            'bs': u'Dodatak',
            'cy': u'WiciSawrws',
            'de': u'Thesaurus',
            'en': u'Index',
            'fr': u'Portail',
            'pl': u'Portal',
            'pt': u'Rimas',
            'ru': [u'Индекс', u'Index'],
            'sv': u'Rimord',
        }

        self.namespaces[105] = {
            'bs': u'Razgovor o Dodatku',
            'cy': u'Sgwrs WiciSawrws',
            'de': u'Thesaurus Diskussion',
            'en': u'Index talk',
            'fr': u'Discussion Portail',
            'pl': u'Dyskusja portalu',
            'pt': u'Rimas Discussão',
            'ru': [u'Обсуждение индекса', u'Index talk'],
            'sv': u'Rimordsdiskussion',
        }

        self.namespaces[106] = {
            'en': u'Rhymes',
            'fr': u'Thésaurus',
            'is': u'Viðauki',
            'pt': u'Portal',
            'ru': [u'Рифмы', u'Rhymes'],
            'sv': u'Transwiki',
        }

        self.namespaces[107] = {
            'en': u'Rhymes talk',
            'fr': u'Discussion Thésaurus',
            'is': u'Viðaukaspjall',
            'pt': u'Portal Discussão',
            'ru': [u'Обсуждение рифм', u'Rhymes talk'],
            'sv': u'Transwikidiskussion',
        }

        self.namespaces[108] = {
            'en': u'Transwiki',
            'pt': u'Citações',
        }

        self.namespaces[109] = {
            'en': u'Transwiki talk',
            'pt': u'Citações Discussão',
        }

        self.namespaces[110] = {
            'en': u'Wikisaurus',
            'is': u'Samheitasafn',
            'ko': u'미주알고주알',
        }

        self.namespaces[111] = {
            'en': u'Wikisaurus talk',
            'is': u'Samheitasafnsspjall',
            'ko': u'미주알고주알 토론',
        }

        self.namespaces[112] = {
         #   'en': u'WT',
        }

        self.namespaces[113] = {
         #   'en': u'WT talk',
        }

        self.namespaces[114] = {
            'en': u'Citations',
        }

        self.namespaces[115] = {
            'en': u'Citations talk',
        }

        # Other than most Wikipedias, page names must not start with a capital
        # letter on ALL Wiktionaries.
        self.nocapitalize = self.langs.keys()

        # Global bot allowed languages on http://meta.wikimedia.org/wiki/Bot_policy/Implementation#Current_implementation
        self.cross_allowed = [
            'ang', 'ast', 'az', 'bg', 'bn', 'da', 'eo', 'es', 'fa', 'fy', 'ga', 'gd', 'hu', 
            'ia', 'ie', 'ik', 'jv', 'ka', 'li', 'lt', 'mk', 'nl', 'no', 'oc', 'pt', 'sk', 'tg', 'th', 'ti', 
            'ts', 'ug', 'uk', 'vo', 'za', 'zh-min-nan', 'zh', 'zu', 
        ]
        # CentralAuth cross avaliable projects.
        self.cross_projects = [
            'wikipedia', 'wikibooks', 'wikiquote', 'wikisource', 'wikinews', 'wikiversity',
            'meta', 'mediawiki', 'test', 'incubator', 'commons', 'species'
        ]
        self.obsolete = {
            'aa': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Afar_Wiktionary
            'ab': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Abkhaz_Wiktionary
            'ak': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Akan_Wiktionary
            'as': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Assamese_Wiktionary
            'av': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Avar_Wiktionary
            'ba': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Bashkir_Wiktionary
            'bh': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Bihari_Wiktionary
            'bi': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Bislama_Wiktionary
            'bm': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Bambara_Wiktionary
            'bo': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Tibetan_Wiktionary
            'ch': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Chamorro_Wiktionary
            'cr': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Nehiyaw_Wiktionary
            'dk': 'da',
            'jp': 'ja',
            'mh': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Marshallese_Wiktionary
            'mo': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Moldovan_Wiktionary
            'minnan':'zh-min-nan',
            'nb': 'no',
            'or': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Oriya_Wiktionary
            'pi': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Pali_Bhasa_Wiktionary
            'rm': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Rhaetian_Wiktionary
            'rn': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Kirundi_Wiktionary
            'sc': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Sardinian_Wiktionary
            'sn': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Shona_Wiktionary
            'to': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Tongan_Wiktionary
            'tlh': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Klingon_Wiktionary
            'tw': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Twi_Wiktionary
            'tokipona': None,
            'xh': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Xhosa_Wiktionary
            'yo': None, # http://meta.wikimedia.org/wiki/Proposals_for_closing_projects/Closure_of_Yoruba_Wiktionary
            'zh-tw': 'zh',
            'zh-cn': 'zh'
        }

        # Order for fy: alphabetical by code, but y counts as i
        # TODO: This code is duplicated from wikipedia_family.py
        def fycomp(x,y):
            x = x.replace("y","i")+x.count("y")*"!"
            y = y.replace("y","i")+y.count("y")*"!"
            return cmp(x,y)
        self.fyinterwiki = self.alphabetic[:]
        self.fyinterwiki.sort(fycomp)

        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.

        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'et': self.alphabetic,
            'fi': self.alphabetic,
            'fy': self.fyinterwiki,
            'he': ['en'],
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
        }

        self.interwiki_on_one_line = ['pl']

        self.interwiki_attop = ['pl']

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
            return '/%s/%s/w' % (self.name, code)

        def nicepath(self, code):
            return '/%s/%s/wiki/' % (self.name, code)
