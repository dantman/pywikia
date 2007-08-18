# -*- coding: utf-8  -*-
import family, config

__version__ = '$Id$'

# The wikimedia family that is known as Wikisource

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikisource'
       
        self.langs = {
            '-':'wikisource.org',
            'dk':'da.wikisource.org',
            'jp':'ja.wikisource.org',
            'minnan':'zh-min-nan.wikisource.org',
            'nb':'no.wikisource.org',
            'tokipona':'tokipona.wikisource.org',
            'zh-cn':'zh.wikisource.org',
            'zh-tw':'zh.wikisource.org'
            }
          
        for lang in self.knownlanguages:
            if lang not in self.langs:
                self.langs[lang] = lang+'.wikisource.org'

        self.namespaces[4] = {
            '_default': [u'Wikisource', self.namespaces[4]['_default']],
            'ang': u'Wicifruma',
            'ar': u'ويكي مصدر',
            'az': u'VikiMənbə',
            'bs': u'Wikizvor',
            'ca': u'Viquitexts',
            'cy': u'Wicitestun',
            'el': u'Βικιθήκη',
            'et': u'Vikitekstid',
            'fa': u'ویکی‌نبشت',
            'fi': u'Wikiaineisto',
            'fo': u'Wikiheimild',
            'he': u'ויקיטקסט',
            'hr': u'Wikizvor',
            'ht': u'Wikisòrs',
            'hu': u'Wikiforrás',
            'is': u'Wikiheimild',
            'la': u'Vicifons',
            'lt': u'Vikišaltiniai',
            'no': u'Wikikilden',
            'pl': u'Wikiźródła',
            'ru': u'Викитека',
            'sl': u'Wikivir',
            'sr': u'Викизворник',
            'th': u'วิกิซอร์ซ',
            'tr': u'VikiKaynak',
            'yi': u'װיקיביבליאָטעק',
        }
        self.namespaces[5] = {
            '_default': [u'Wikisource talk', self.namespaces[5]['_default']],
            'ang': u'Wicifruma talk',
            'ar': u'نقاش ويكي مصدر',
            'az': u'VikiMənbə müzakirəsi',
            'bg': u'Wikisource беседа',
            'bs': u'Razgovor s Wikizvor',
            'ca': u'Viquitexts Discussió',
            'cs': u'Wikisource diskuse',
            'cy': u'Sgwrs Wicitestun',
            'da': u'Wikisource diskussion',
            'de': u'Wikisource Diskussion',
            'el': u'Βικιθήκη συζήτηση',
            'es': u'Wikisource Discusión',
            'et': u'Vikitekstid arutelu',
            'fa': u'بحث ویکی‌نبشت',
            'fi': u'Keskustelu Wikiaineistosta',
            'fo': u'Wikiheimild kjak',
            'fr': u'Discussion Wikisource',
            'he': u'שיחת ויקיטקסט',
            'hr': u'Razgovor o Wikizvoru',
            'ht': u'Wikisòrs talk',
            'hu': u'Wikiforrás vita',
            'id': u'Pembicaraan Wikisource',
            'is': u'Wikiheimildspjall',
            'it': u'Discussioni Wikisource',
            'ja': u'Wikisource‐ノート',
            'ko': u'Wikisource토론',
            'la': u'Disputatio Vicifontis',
            'lt': u'Vikišaltiniai aptarimas',
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
            'te': u'Wikisource చర్చ',
            'th': u'คุยเรื่องวิกิซอร์ซ',
            'tr': u'VikiKaynak tartışma',
            'uk': u'Обговорення Wikisource',
            'vi': u'Thảo luận Wikisource',
            'yi': u'װיקיביבליאָטעק רעדן',
        }
        self.namespaces[100] = {
            '_default': u'Portal',
            'nl': u'Hoofdportaal',
        }
        self.namespaces[101] = {
            '_default': u'Portal talk',
            'nl': u'Overleg hoofdportaal',
            'pt': u'Portal Discussão',
        }
        self.namespaces[102] = {
            '_default': u'Author',
            'it': u'Autore',
            'la': u'Scriptor',
            'pt': u'Autor',
        }
        self.namespaces[103] = {
            '_default': u'Author talk',
            'it': u'Discussioni autore',
            'la': u'Disputatio Scriptoris',
            'pt': u'Autor Discussão',
        }

        self.namespaces[104] = {
            '_default': u'Page',
            'en': u'Page',
        }

        self.namespaces[105] = {
            '_default': u'Page talk',
            'en': u'Page talk',
        }
        
        self.alphabetic = ['ang','ar','az','bg','bs','ca','cs','cy',
                      'da','de','el','en','es','et','fa','fi',
                      'fo','fr','gl','he','hr','ht','hu','id',
                      'is','it','ja', 'ko','la','lt','ml','nl',
                      'no','pl','pt','ro','ru','sk','sl','sr',
                      'sv','te','th','tr','uk','vi','yi','zh']

    def version(self, code): 	 
        return "1.11"
    def shared_image_repository(self, code):
        return ('commons', 'commons')

