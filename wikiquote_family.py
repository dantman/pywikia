# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as Wikiquote

class Family(family.Family):

    def __init__(self):
        # Known wiktionary languages, given as a dictionary mapping the language code
        # to the hostname of the site hosting that wiktionary. For human consumption,
        # the full name of the language is given behind each line as a comment
        self.langs = {
            'af':'af.wikiquote.org',   # Afrikaans
            'als':'als.wikiquote.org', # Alsatian
            'ar':'ar.wikiquote.org',   # Arabic
            'az':'az.wikiquote.org',   # Azerbaijan
            'be':'be.wikiquote.org',   # Belorussian
            'bg':'bg.wikiquote.org',   # Bulgarian
            'bi':'bi.wikiquote.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
            'bn':'bn.wikiquote.org',   # Bengali
            'bs':'bs.wikiquote.org',   # Bosnian
            'ca':'ca.wikiquote.org',   # Catalan
            'chr':'chr.wikiquote.org', # Cherokee
            'co':'co.wikiquote.org',   # Corsican
            'cs':'cs.wikiquote.org',   # Czech
            'csb':'csb.wikiquote.org', # Kashubian
            'cy':'cy.wikiquote.org',   # Welsh
            'da':'da.wikiquote.org',   # Danish
            'de':'de.wikiquote.org',   # German
            'dk':'da.wikiquote.org',   # Danish (wrong name)
            'el':'el.wikiquote.org',   # Greek
            'en':'en.wikiquote.org',   # English
            'eo':'eo.wikiquote.org',   # Esperanto
            'es':'es.wikiquote.org',   # Spanish
            'et':'et.wikiquote.org',   # Estonian
            'eu':'eu.wikiquote.org',   # Basque
            'fa':'fa.wikiquote.org',   # Farsi
            'fi':'fi.wikiquote.org',   # Finnish
            'fo':'fo.wikiquote.org',   # Faroese
            'fr':'fr.wikiquote.org',   # French
            'fy':'fy.wikiquote.org',   # Frisian
            'ga':'ga.wikiquote.org',   # Irish Gaelic
            'gd':'gd.wikiquote.org',   # Scottish Gaelic
            'gl':'gl.wikiquote.org',   # Galician
            'gn':'gn.wikiquote.org',   # Guarani
            'gv':'gv.wikiquote.org',   # Manx
            'he':'he.wikiquote.org',   # Hebrew
            'hi':'hi.wikiquote.org',   # Hindi
            'hr':'hr.wikiquote.org',   # Croatian
            'hu':'hu.wikiquote.org',   # Hungarian
            'ia':'ia.wikiquote.org',   # Interlingua
            'id':'id.wikiquote.org',   # Indonesian
            'io':'io.wikiquote.org',   # Ido
            'is':'is.wikiquote.org',   # Icelandic
            'it':'it.wikiquote.org',   # Italian
            'ja':'ja.wikiquote.org',   # Japanese
            'jv':'jv.wikiquote.org',   # Javanese
            'ka':'ka.wikiquote.org',   # Georgian
            'km':'km.wikiquote.org',   # Khmer
            'ko':'ko.wikiquote.org',   # Korean
            'ks':'ks.wikiquote.org',   # Ekspreso, but should become Kashmiri
            'ku':'ku.wikiquote.org',   # Kurdish
            'la':'la.wikiquote.org',   # Latin
            'lt':'lt.wikiquote.org',   # Latvian
            'lv':'lv.wikiquote.org',   # Livonian
            'mg':'mg.wikiquote.org',   # Malagasy
            'mi':'mi.wikiquote.org',   # Maori
            'minnan':'minnan.wikiquote.org', # Min-Nan
            'mk':'mk.wikiquote.org',   # Macedonian
            'ml':'ml.wikiquote.org',   # Malayalam
            'mn':'mn.wikiquote.org',   # Mongolian
            'mr':'mr.wikiquote.org',   # Marathi
            'ms':'ms.wikiquote.org',   # Malay
            'na':'na.wikiquote.org',   # Nauruan
            'nah':'nah.wikiquote.org', # Nahuatl
            'nb':'no.wikiquote.org',   # Norse - new code for Bokmal to distinguish from Nynorsk
            'nds':'nds.wikiquote.org', # Lower Saxon
            'nl':'nl.wikiquote.org',   # Dutch
            'no':'no.wikiquote.org',   # Norwegian
            'oc':'oc.wikiquote.org',   # Occitan
            'om':'om.wikiquote.org',   # Oromo
            'pl':'pl.wikiquote.org',   # Polish
            'pt':'pt.wikiquote.org',   # Portuguese
            'ro':'ro.wikiquote.org',   # Romanian
            'roa-rup':'roa-rup.wikiquote.org', # Aromanian
            'ru':'ru.wikiquote.org',   # Russian
            'sa':'sa.wikiquote.org',   # Sanskrit
            'sh':'sh.wikiquote.org',   # OBSOLETE, Serbocroatian
            'si':'si.wikiquote.org',   # Sinhalese
            'simple':'simple.wikiquote.org', # Simple English
            'sk':'sk.wikiquote.org',   # Slovakian
            'sl':'sl.wikiquote.org',   # Slovenian
            'sq':'sq.wikiquote.org',   # Albanian
            'sr':'sr.wikiquote.org',   # Serbian
            'st':'st.wikiquote.org',   # Sesotho
            'su':'su.wikiquote.org',   # Sundanese
            'sv':'sv.wikiquote.org',   # Swedish
            'sw':'sw.wikiquote.org',   # Swahili
            'ta':'ta.wikiquote.org',   # Tamil
            'test':'test.wikiquote.org',
            'th':'th.wikiquote.org',   # Thai
            'tl':'tl.wikiquote.org',   # Tagalog
            'tlh':'tlh.wikiquote.org', # Klingon
            'tokipona':'tokipona.wikiquote.org', # Toki Pona
            'tpi':'tpi.wikiquote.org', # Tok Pisin
            'tr':'tr.wikiquote.org',   # Turkish
            'tt':'tt.wikiquote.org',   # Tatar
            'uk':'uk.wikiquote.org',   # Ukrainian
            'ur':'ur.wikiquote.org',   # Urdu
            'vi':'vi.wikiquote.org',   # Vietnamese
            'vo':'vo.wikiquote.org',   # Volapuk
            'wa':'wa.wikiquote.org',   # Walon
            'xh':'xh.wikiquote.org',   # isiXhosa
            'yi':'yi.wikiquote.org',   # Yiddish
            'yo':'yo.wikiquote.org',   # Yoruba
            'za':'za.wikiquote.org',   # Zhuang
            'zh':'zh.wikiquote.org',   # Chinese
            'zh-cn':'zh.wikiquote.org', # Simplified Chinese
            'zh-tw':'zh.wikiquote.org', # Traditional Chinese
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
                '_default': u'Wikiquote',
            },
            5: {
                '_default': u'Wikiquote talk',
                'de': u'Wikiquote Diskussion',
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
