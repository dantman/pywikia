# -*- coding: utf-8  -*-
import family

# The Anarchopedia family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'anarchopedia'

        interface_lang = {
            'ara': 'ar',
            'bos': 'sr',
            'dan': 'da',
            'deu': 'de',
            'dut': 'nl',
            'ell': 'el',
            'eng': 'en',
            'epo': 'en',
            'fas': 'fa',
            'fin': 'fi',
            'fra': 'fr',
            'heb': 'he',
            'hrv': 'sr',
            'hye': 'hy',
            'ind': 'id',
            'ita': 'it',
            'jpn': 'ja',
            'kor': 'ko',
            'lav': 'lv',
            'lit': 'lit',
            'nor': 'no',
            'nsh': 'sr',
            'pol': 'pl',
            'por': 'pt',
            'rum': 'ro',
            'rus': 'ru',
            'spa': 'es',
            'sqi': 'sq',
            'srp': 'sr',
            'swe': 'sv',
            'tur': 'tr',
            'zho': 'zh',
        }

        for lang in interface_lang.values():
            self.langs[lang] = '%s.anarchopedia.org' % lang

        copy = [-2, -1, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for code, interface in interface_lang.items():
            for ns in copy:
                if self.namespaces[ns].has_key(interface):
                    self.namespaces[ns][code] = self.namespaces[ns][interface]

        self.namespaces[4] = {
            '_default': [u'Anarchopedia', self.namespaces[4]['_default']],
            'ar': u'أنارشوبيديا',
            'el': u'Αναρχοπαίδεια',
            'ja': u'アナーキォペディア',
            'ro': u'Anarhopedia',
            'he': u'אנרכופדיה',
            'zh': u'安那其百科',
            'ko': u'아나코백과',
            'sr': u'Anarhopedija / Анархопедија',
            'eo': u'Anarĥopedio',
            'ru': u'Анархопедия',
            'hy': u'Անարխոպեդիա',
            'it': u'Anarcopedia',
            'pt': u'Anarcopédia',
            'tr': u'Anarşipedi',
        }
        self.namespaces[5] = {
            '_default': [u'Anarchopedia talk', self.namespaces[5]['_default']],
            'ar': u'نقاش أنارشوبيديا',
            'bs': u'Разговор о Anarchopedia',
            'zh': u'安那其百科 talk',
            'da': u'Anarchopedia-diskussion',
            'de': u'Anarchopedia Diskussion',
            'nl': u'Overleg Anarchopedia',
            'el': u'Αναρχοπαίδεια συζήτηση',
            'fi': u'Keskustelu Anarchopediasta',
            'fr': u'Discussion Anarchopedia',
            'he': u'שיחת אנרכופדיה',
            'id': u'Pembicaraan Anarchopedia',
            'it': u'Discussioni Anarchopedia',
            'ja': u'アナーキォペディア‐ノート' ,
            'no': u'Anarchopedia-diskusjon' ,
            'sh': u'Разговор о Anarhopedija / Анархопедија',
            'or': u'Anarchopedia-diskusjon',
            'pl': u'Dyskusja Anarchopedia',
            'pt': u'Anarchopedia Discussão',
            'ro': u'Discuţie Anarhopedia',
            'ru': u'Обсуждение Anarchopedia',
            'es': u'Anarchopedia Discusión',
            'sr': u'Разговор о Anarchopedia',
            'sv': u'Anarchopediadiskussion',
            'tr': u'Anarşipedi tartışma',
        }

        self.nocapitalize = self.langs.keys()

        self.obsolete = {
            'ara': 'ar',
            'bos': 'bs',
            'zho': 'zh',
            'dan': 'da',
            'deu': 'de',
            'dut': 'nl',
            'ell': 'el',
            'eng': 'en',
            'epo': 'eo',
            'fas': 'fa',
            'fra': 'fr',
            'fin': 'fi',
            'heb': 'he',
            'ind': 'id',
            'ita': 'it',
            'jpn': 'ja',
            'lit': 'lt',
            'lav': 'lv',
            'nor': 'no',
            'nsh': 'sh',
            'pol': 'pl',
            'por': 'pt',
            'rum': 'ro',
            'rus': 'ru',
            'spa': 'es',
            'srp': 'sr',
            'srp': 'hr',
            'swe': 'sv',
            'kor': 'ko',
            'sqi': 'sq',
            'hye': 'hy',
            'tur': 'tr',

            'ell': 'gre',
            'srp': 'hrv',
            'nno': None,
            'nob': None,
        }

    def version(self, code):
        return "1.14alpha"

    def scriptpath(self, code):
        return ''

    def api_address(self, code):
        raise NotImplementedError('Anarchopedia has not activated the API')
        
