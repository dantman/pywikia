# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as wiktionary

# Known wiktionary languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wiktionary. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):

    def __init__(self):
        self.langs = {
            'af':'af.wiktionary.org',   # Afrikaans
            'als':'als.wiktionary.org', # Alsatian
            'ar':'ar.wiktionary.org',   # Arabic
            'az':'az.wiktionary.org',   # Azerbaijan
            'be':'be.wiktionary.org',   # Belorussian
            'bg':'bg.wiktionary.org',   # Bulgarian
            'bi':'bi.wiktionary.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
            'bn':'bn.wiktionary.org',   # Bengali
            'bs':'bs.wiktionary.org',   # Bosnian
            'ca':'ca.wiktionary.org',   # Catalan
            'chr':'chr.wiktionary.org', # Cherokee
            'co':'co.wiktionary.org',   # Corsican
            'cs':'cs.wiktionary.org',   # Czech
            'csb':'csb.wiktionary.org', # Kashubian
            'cy':'cy.wiktionary.org',   # Welsh
            'da':'da.wiktionary.org',   # Danish
            'de':'de.wiktionary.org',   # German
            'el':'el.wiktionary.org',   # Greek
            'en':'en.wiktionary.org',   # English
            'eo':'eo.wiktionary.org',   # Esperanto
            'es':'es.wiktionary.org',   # Spanish
            'et':'et.wiktionary.org',   # Estonian
            'eu':'eu.wiktionary.org',   # Basque
            'fa':'fa.wiktionary.org',   # Farsi
            'fi':'fi.wiktionary.org',   # Finnish
            'fr':'fr.wiktionary.org',   # French
            'fy':'fy.wiktionary.org',   # Frisian
            'ga':'ga.wiktionary.org',   # Irish Gaelic
            'gd':'gd.wiktionary.org',   # Scottish Gaelic
            'gl':'gl.wiktionary.org',   # Galician
            'gn':'gn.wiktionary.org',   # Guarani
            'gv':'gv.wiktionary.org',   # Manx
            'he':'he.wiktionary.org',   # Hebrew
            'hi':'hi.wiktionary.org',   # Hindi
            'hr':'hr.wiktionary.org',   # Croatian
            'hu':'hu.wiktionary.org',   # Hungarian
            'ia':'ia.wiktionary.org',   # Interlingua
            'id':'id.wiktionary.org',   # Indonesian
            'io':'io.wiktionary.org',   # Ido
            'is':'is.wiktionary.org',   # Icelandic
            'it':'it.wiktionary.org',   # Italian
            'ja':'ja.wiktionary.org',   # Japanese
            'jv':'jv.wiktionary.org',   # Javanese
            'ka':'ka.wiktionary.org',   # Georgian
            'ko':'ko.wiktionary.org',   # Korean
            'ks':'ks.wiktionary.org',   # Ekspreso, but should become Kashmiri
            'ku':'ku.wiktionary.org',   # Kurdish
            'la':'la.wiktionary.org',   # Latin
            'lt':'lt.wiktionary.org',   # Latvian
            'lv':'lv.wiktionary.org',   # Livonian
            'mg':'mg.wiktionary.org',   # Malagasy
            'mi':'mi.wiktionary.org',   # Maori
            'minnan':'minnan.wiktionary.org', # Min-Nan
            'mk':'mk.wiktionary.org',   # Macedonian
            'ml':'ml.wiktionary.org',   # Malayalam
            'mn':'mn.wiktionary.org',   # Mongolian
            'mr':'mr.wiktionary.org',   # Marathi
            'ms':'ms.wiktionary.org',   # Malay
            'na':'na.wiktionary.org',   # Nauruan
            'nah':'nah.wiktionary.org', # Nahuatl
            'nb':'no.wiktionary.org',   # Norse - new code for Bokmal to distinguish from Nynorsk
            'nds':'nds.wiktionary.org', # Lower Saxon
            'nl':'nl.wiktionary.org',   # Dutch
            'no':'no.wiktionary.org',   # Norwegian
            'oc':'oc.wiktionary.org',   # Occitan
            'om':'om.wiktionary.org',   # Oromo
            'pl':'pl.wiktionary.org',   # Polish
            'pt':'pt.wiktionary.org',   # Portuguese
            'ro':'ro.wiktionary.org',   # Romanian
            'roa-rup':'roa-rup.wiktionary.org', # Aromanian
            'ru':'ru.wiktionary.org',   # Russian
            'sa':'sa.wiktionary.org',   # Sanskrit
            'si':'si.wiktionary.org',   # Sinhalese
            'simple':'simple.wiktionary.org', # Simple English
            'sk':'sk.wiktionary.org',   # Slovakian
            'sl':'sl.wiktionary.org',   # Slovenian
            'sq':'sq.wiktionary.org',   # Albanian
            'sr':'sr.wiktionary.org',   # Serbian
            'st':'st.wiktionary.org',   # Sesotho
            'su':'su.wiktionary.org',   # Sundanese
            'sv':'sv.wiktionary.org',   # Swedish
            'sw':'sw.wiktionary.org',   # Swahili
            'ta':'ta.wiktionary.org',   # Tamil
            'th':'th.wiktionary.org',   # Thai
            'tl':'tl.wiktionary.org',   # Tagalog
            'tlh':'tlh.wiktionary.org', # Klingon
            'tokipona':'tokipona.wiktionary.org', # Toki Pona
            'tpi':'tpi.wiktionary.org', # Tok Pisin
            'tr':'tr.wiktionary.org',   # Turkish
            'tt':'tt.wiktionary.org',   # Tatar
            'uk':'uk.wiktionary.org',   # Ukrainian
            'ur':'ur.wiktionary.org',   # Urdu
            'vi':'vi.wiktionary.org',   # Vietnamese
            'vo':'vo.wiktionary.org',   # Volapuk
            'wa':'wa.wiktionary.org',   # Walon
            'xh':'xh.wiktionary.org',   # isiXhosa
            'yi':'yi.wiktionary.org',   # Yiddish
            'yo':'yo.wiktionary.org',   # Yoruba
            'za':'za.wiktionary.org',   # Zhuang
            'zh':'zh.wiktionary.org',   # Chinese
            'zh-cn':'zh.wiktionary.org', # Simplified Chinese
            'zh-tw':'zh.wiktionary.org', # Traditional Chinese
            }

        # Translation used on all Wikipedias for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces = {
            -2: {
                '_default': u'Media',
            },
            -1: {
                '_default': u'Special',
                'af': u'Spesiaal',
                'ar': u'خاص',
                'bg': u'Специални',
                'bn': u'বিশেষ',
                'ca': u'Especial',
                'cs': u'Speciální',
                'csb': u'Specjalnô',
                'cy': u'Arbennig',
                'da': u'Speciel',
                'de': u'Spezial',
                'eo': u'Speciala',
                'es': u'Especial',
                'et': u'Eri',
                'fa': u'ویژه',
                'fi': u'Toiminnot',
                'fy': u'Wiki',
                'ga': u'Speisialta',
                'he': u'מיוחד',
                'hi': u'विशेष',
                'hu': u'Speciális',
                'id': u'Istimewa',
                'it': u'Speciale',
                'ja': u'特別',
                'ko': u'특수기능',
                'la': u'Specialis',
                'ms': u'Istimewa',
                'nb': u'Spesial',
                'nl': u'Speciaal',
                'no': u'Spesial',
                'oc': u'Especial',
                'pl': u'Specjalna',
                'pt': u'Especial',
                'ru': u'Специальные',
                'sk': u'Špeciálne',
                'sl': u'Posebno',
                'sq': u'Speciale',
                'sr': u'Посебно',
                'uk': u'Спеціальні',
                'ta': u'சிறப்பு',
                'th': u'พิเศษ',
                'wa': u'Sipeciås',
            },
            0: {
                '_default': None,
            },
            1: {
                '_default': 'Talk',
                'de': u'Diskussion',
                'nl': u'Overleg',
            },
            2: {
                '_default': u'User',
                'de': u'Benutzer',
                'nl': u'Gebruiker',
            },
            3: {
                '_default': u'User talk',
                'de': u'Benutzer Diskussion',
            },
            4: {
                '_default': u'Wiktionary',
            },
            5: {
                '_default': u'Wiktionary talk',
                'de': u'Wiktionary Diskussion',
            },
            6: {
                # TODO: convert all percent-encoded titles to plaintext
                '_default': u'Image',
                'af': u'Beeld',
                'ar': u'صورة',
                'bg': u'Картинка',
                #'bn': To be checked,
                'ca': u'Imatge',
                'cs': u'Soubor',
                'csb': u'Òbrôzk',
                'cy': u'Delwedd',
                'da': u'Billede',
                'de': u'Bild',
                'eo': u'Dosiero',
                'es': u'Imagen',
                'et': u'Pilt',
                'fa': u'تصویر',
                'fi': u'Kuva',
                'fr': u'Image',
                'fy': u'Ofbyld',
                'ga': u'Íomhá',
                'he': u'תמונה',
                'hi': u'चित्र',
                'hu': u'Kép',
                'ia': u'Imagine',
                'id': u'Imej',
                'it': u'Immagine',
                'ja': u'画像',
                'ko': u'그림',
                'la': u'Imago',
                'ms': u'Imej',
                'nb': u'Bilde',
                'nl': u'Afbeelding',
                'no': u'Bilde',
                'oc': u'Image',
                'pl': u'Grafika',
                'pt': u'Imagem',
                'ro': u'Imagine',
                'ru': u'Изображение',
                'sk': u'Obrázok',
                'sl': u'Slika',
                'sq': u'Figura',
                'sr': u'Слика',
                'sv': u'Bild',
                'ta': u'படிமம்',
                'th': u'ภาพ',
                'wa': u'Imådje',
            },
            7: {
                '_default': u'Image talk',
                'de': u'Bild Diskussion',        
            },
            8: {
                '_default': u'MediaWiki',
                'bg': u'МедияУики',
            },
            9: {
                '_default': u'MediaWiki talk',
                'de': u'MediaWiki Diskussion',
            },
            10: {
                '_default':u'Template',
                'de':u'Vorlage',
                'nl':u'Sjabloon'
            },
            11: {
                '_default': u'Template talk',
                'de': u'Vorlage Diskussion',
            },
            12: {
                '_default': u'Help',
                'de': u'Hilfe',
            },
            13: {
                '_default': u'Help talk',
                'de': u'Hilfe Diskussion',
            },
            14: {
                '_default': u'Category',
                'da': u'Kategori',
                'de': u'Kategorie',
                'es': u'Categoría',
                'fr': u'Catégorie',
                'hu': u'Kategória',
                'is': u'Flokkur',
                'nl': u'Categorie',
                'no': u'Kategori',
                'sv': u'Kategori',
            },
            15: {
                '_default': u'Category talk',
                'de': u'Kategorie Diskussion',        
            },
        }
        
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.
        
        self.alphabetic = ['af','ar','roa-rup','om','bg','be','bn','bs',
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
            'en': self.alphabetic,
            'fr': self.alphabetic,
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic
            }
        
        # group of languages that we might want to do at once
        
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
       
        # Function to figure out the encoding of different languages
        # Languages that are coded in iso-8859-1
        self.latin1 = ['es']
    
    def code2encoding(self, code):
        """Return the encoding for a specific language wiktionary"""
        if code == 'ascii':
            return 'ascii' # Special case where we do not want special characters.
        if code in self.latin1:
            return 'iso-8859-1'
        return 'utf-8'
    
    def code2encodings(self, code):
        """Return a list of historical encodings for a specific language
           wiktionary"""
        return self.code2encoding(code),
