# -*- coding: utf-8  -*-
import family

# The Anarchopedia family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'anarchopedia'

        self.langs = {
            'ara': 'ara.anarchopedia.org',
            'ar':  'ara.anarchopedia.org',
            'bos': 'bos.anarchopedia.org',
            'bs':  'bos.anarchopedia.org',
            'chi': 'chi.anarchopedia.org',
            'zh':  'chi.anarchopedia.org',
            'dan': 'dan.anarchopedia.org',
            'da':  'dan.anarchopedia.org',
            'deu': 'deu.anarchopedia.org',
            'ger': 'deu.anarchopedia.org',
            'de':  'deu.anarchopedia.org',
            'dut': 'dut.anarchopedia.org',
            'nl':  'dut.anarchopedia.org',
            'ell': 'ell.anarchopedia.org',
            'gre': 'ell.anarchopedia.org',
            'el':  'ell.anarchopedia.org',
            'eng': 'eng.anarchopedia.org',
            'en':  'eng.anarchopedia.org',
            'epo': 'epo.anarchopedia.org',
            'eo':  'epo.anarchopedia.org',
            'fra': 'fra.anarchopedia.org',
            'fr':  'fra.anarchopedia.org',
            'ind': 'ind.anarchopedia.org',
            'id':  'ind.anarchopedia.org',
            'ita': 'ita.anarchopedia.org',
            'it':  'ita.anarchopedia.org',
            'jpn': 'jpn.anarchopedia.org',
            'ja':  'jpn.anarchopedia.org',
            'lit': 'lit.anarchopedia.org',
            'lt':  'lit.anarchopedia.org',
            'nno': 'nno.anarchopedia.org',
            'nn':  'nno.anarchopedia.org',
            'nsh': 'nsh.anarchopedia.org',
            'sh':  'nsh.anarchopedia.org',
            'nor': 'nor.anarchopedia.org',
            'no':  'nor.anarchopedia.org',
            'pol': 'pol.anarchopedia.org',
            'pl':  'pol.anarchopedia.org',
            'por': 'por.anarchopedia.org',
            'pt':  'por.anarchopedia.org',
            'rum': 'rum.anarchopedia.org',
            'ro':  'rum.anarchopedia.org',
            'rus': 'rus.anarchopedia.org',
            'ru':  'rus.anarchopedia.org',
            'spa': 'spa.anarchopedia.org',
            'es':  'spa.anarchopedia.org',
            'srp': 'srp.anarchopedia.org',
            'sr':  'srp.anarchopedia.org',
            'hrv': 'srp.anarchopedia.org',
            'hr':  'srp.anarchopedia.org',
            'swe': 'swe.anarchopedia.org',
            'sv':  'swe.anarchopedia.org',
        }

        interface_lang = {
            'ara': 'ar',
            'bos': 'sr',
            'chi': 'zh',
            'dan': 'da',
            'deu': 'de',
            'dut': 'nl',
            'ell': 'el',
            'eng': 'en',
            'epo': 'en',
            'fra': 'fr',
            'hrv': 'sr',
            'ind': 'id',
            'ita': 'it',
            'jpn': 'ja',
            'lit': 'lit',
            'nno': 'nn',
            'nor': 'no',
            'nsh': 'sr',
            'pol': 'pl',
            'por': 'pt',
            'rum': 'ro',
            'rus': 'ru',
            'spa': 'es',
            'srp': 'sr',
            'swe': 'sv',
        }
        copy = [-2, -1, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for code, interface in interface_lang.items():
            for ns in copy:
                if self.namespaces[ns].has_key(interface):
                    self.namespaces[ns][code] = self.namespaces[ns][interface]

        self.namespaces[4] = {
            '_default': [u'Anarchopedia', self.namespaces[4]['_default']],
            'ara': u'أنارشوبيديا',
            'chi': u'安那其百科',
            'ell': u'Αναρχοπαίδεια',
            'jpn': u'アナーキォペディア',
            'rum': u'Anarhopedia',
        }
        self.namespaces[5] = {
            '_default': [u'Anarchopedia talk', self.namespaces[5]['_default']],
            'ara': u'نقاش أنارشوبيديا',
            'bos': u'Разговор о Anarchopedia',
            'chi': u'安那其百科 talk',
            'dan': u'Anarchopedia-diskussion',
            'deu': u'Anarchopedia Diskussion',
            'dut': u'Overleg Anarchopedia',
            'ell': u'Αναρχοπαίδεια συζήτηση',
            'fra': u'Discussion Anarchopedia',
            'ind': u'Pembicaraan Anarchopedia',
            'ita': u'Discussioni Anarchopedia',
            'jpn': u'アナーキォペディア‐ノート',
            'nno': u'Anarchopedia-diskusjon',
            'nsh': u'Разговор о Anarchopedia',
            'nor': u'Anarchopedia-diskusjon',
            'pol': u'Dyskusja Anarchopedia',
            'por': u'Anarchopedia Discussão',
            'rum': u'Discuţie Anarhopedia',
            'rus': u'Обсуждение Anarchopedia',
            'spa': u'Anarchopedia Discusión',
            'srp': u'Разговор о Anarchopedia',
            'swe': u'Anarchopediadiskussion',
        }

        self.nocapitalize = self.langs.keys()

        self.obsolete = {
            'ar': 'ara',
            'bs': 'bos',
            'zh': 'chi',
            'da': 'dan',
            'de': 'deu',
            'ger': 'deu',
            'nl': 'dut',
            'el': 'ell',
            'gre': 'ell',
            'en': 'eng',
            'eo': 'epo',
            'fr': 'fra',
            'id': 'ind',
            'it': 'ita',
            'ja': 'jpn',
            'lt': 'lit',
            'no': 'nor',
            'nn': 'nno',
            'sh': 'nsh',
            'pl': 'pol',
            'pt': 'por',
            'ro': 'rum',
            'ru': 'rus',
            'es': 'spa',
            'sr': 'srp',
            'hrv': 'srp',
            'hr': 'srp',
            'sv': 'swe',
        }

    def version(self, code):
        return "1.12alpha"

    def path(self, code):
        return '/index.php'
