# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as Wikibooks

class Family(family.Family):

    def __init__(self):
        # Known wikibooks languages, given as a dictionary mapping the language code
        # to the hostname of the site hosting that wiktibooks. For human consumption,
        # the full name of the language is given behind each line as a comment
        self.langs = {
            'af':'af.wikibooks.org',   # Afrikaans
            'als':'als.wikibooks.org', # Alsatian
            'ar':'ar.wikibooks.org',   # Arabic
            'az':'az.wikibooks.org',   # Azerbaijan
            'be':'be.wikibooks.org',   # Belorussian
            'bg':'bg.wikibooks.org',   # Bulgarian
            'bi':'bi.wikibooks.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
            'bn':'bn.wikibooks.org',   # Bengali
            'bs':'bs.wikibooks.org',   # Bosnian
            'ca':'ca.wikibooks.org',   # Catalan
            'chr':'chr.wikibooks.org', # Cherokee
            'co':'co.wikibooks.org',   # Corsican
            'cs':'cs.wikibooks.org',   # Czech
            'csb':'csb.wikibooks.org', # Kashubian
            'cy':'cy.wikibooks.org',   # Welsh
            'da':'da.wikibooks.org',   # Danish
            'de':'de.wikibooks.org',   # German
            'dk':'da.wikibooks.org',   # Danish (wrong name)
            'el':'el.wikibooks.org',   # Greek
            'en':'en.wikibooks.org',   # English
            'eo':'eo.wikibooks.org',   # Esperanto
            'es':'es.wikibooks.org',   # Spanish
            'et':'et.wikibooks.org',   # Estonian
            'eu':'eu.wikibooks.org',   # Basque
            'fa':'fa.wikibooks.org',   # Farsi
            'fi':'fi.wikibooks.org',   # Finnish
            'fo':'fo.wikibooks.org',   # Faroese
            'fr':'fr.wikibooks.org',   # French
            'fy':'fy.wikibooks.org',   # Frisian
            'ga':'ga.wikibooks.org',   # Irish Gaelic
            'gd':'gd.wikibooks.org',   # Scottish Gaelic
            'gl':'gl.wikibooks.org',   # Galician
            'gn':'gn.wikibooks.org',   # Guarani
            'gv':'gv.wikibooks.org',   # Manx
            'he':'he.wikibooks.org',   # Hebrew
            'hi':'hi.wikibooks.org',   # Hindi
            'hr':'hr.wikibooks.org',   # Croatian
            'hu':'hu.wikibooks.org',   # Hungarian
            'ia':'ia.wikibooks.org',   # Interlingua
            'id':'id.wikibooks.org',   # Indonesian
            'io':'io.wikibooks.org',   # Ido
            'is':'is.wikibooks.org',   # Icelandic
            'it':'it.wikibooks.org',   # Italian
            'ja':'ja.wikibooks.org',   # Japanese
            'jv':'jv.wikibooks.org',   # Javanese
            'ka':'ka.wikibooks.org',   # Georgian
            'km':'km.wikibooks.org',   # Khmer
            'ko':'ko.wikibooks.org',   # Korean
            'ks':'ks.wikibooks.org',   # Ekspreso, but should become Kashmiri
            'ku':'ku.wikibooks.org',   # Kurdish
            'la':'la.wikibooks.org',   # Latin
            'lt':'lt.wikibooks.org',   # Latvian
            'lv':'lv.wikibooks.org',   # Livonian
            'mg':'mg.wikibooks.org',   # Malagasy
            'mi':'mi.wikibooks.org',   # Maori
            'minnan':'minnan.wikibooks.org', # Min-Nan
            'mk':'mk.wikibooks.org',   # Macedonian
            'ml':'ml.wikibooks.org',   # Malayalam
            'mn':'mn.wikibooks.org',   # Mongolian
            'mr':'mr.wikibooks.org',   # Marathi
            'ms':'ms.wikibooks.org',   # Malay
            'na':'na.wikibooks.org',   # Nauruan
            'nah':'nah.wikibooks.org', # Nahuatl
            'nb':'no.wikibooks.org',   # Norse - new code for Bokmal to distinguish from Nynorsk
            'nds':'nds.wikibooks.org', # Lower Saxon
            'nl':'nl.wikibooks.org',   # Dutch
            'no':'no.wikibooks.org',   # Norwegian
            'oc':'oc.wikibooks.org',   # Occitan
            'om':'om.wikibooks.org',   # Oromo
            'pl':'pl.wikibooks.org',   # Polish
            'pt':'pt.wikibooks.org',   # Portuguese
            'ro':'ro.wikibooks.org',   # Romanian
            'roa-rup':'roa-rup.wikibooks.org', # Aromanian
            'ru':'ru.wikibooks.org',   # Russian
            'sa':'sa.wikibooks.org',   # Sanskrit
            'sh':'sh.wikibooks.org',   # OBSOLETE, Serbocroatian
            'si':'si.wikibooks.org',   # Sinhalese
            'simple':'simple.wikibooks.org', # Simple English
            'sk':'sk.wikibooks.org',   # Slovakian
            'sl':'sl.wikibooks.org',   # Slovenian
            'sq':'sq.wikibooks.org',   # Albanian
            'sr':'sr.wikibooks.org',   # Serbian
            'st':'st.wikibooks.org',   # Sesotho
            'su':'su.wikibooks.org',   # Sundanese
            'sv':'sv.wikibooks.org',   # Swedish
            'sw':'sw.wikibooks.org',   # Swahili
            'ta':'ta.wikibooks.org',   # Tamil
            'test':'test.wikibooks.org',
            'th':'th.wikibooks.org',   # Thai
            'tl':'tl.wikibooks.org',   # Tagalog
            'tlh':'tlh.wikibooks.org', # Klingon
            'tokipona':'tokipona.wikibooks.org', # Toki Pona
            'tpi':'tpi.wikibooks.org', # Tok Pisin
            'tr':'tr.wikibooks.org',   # Turkish
            'tt':'tt.wikibooks.org',   # Tatar
            'uk':'uk.wikibooks.org',   # Ukrainian
            'ur':'ur.wikibooks.org',   # Urdu
            'vi':'vi.wikibooks.org',   # Vietnamese
            'vo':'vo.wikibooks.org',   # Volapuk
            'wa':'wa.wikibooks.org',   # Walon
            'xh':'xh.wikibooks.org',   # isiXhosa
            'yi':'yi.wikibooks.org',   # Yiddish
            'yo':'yo.wikibooks.org',   # Yoruba
            'za':'za.wikibooks.org',   # Zhuang
            'zh':'zh.wikibooks.org',   # Chinese
            'zh-cn':'zh.wikibooks.org', # Simplified Chinese
            'zh-tw':'zh.wikibooks.org', # Traditional Chinese
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
                'ar': u'Ø®Ø§Øµ',
                'bg': u'Ð¡Ð¿ÐµÑ†Ð¸Ð°Ð»Ð½Ð¸',
                'bn': u'à¦¬à¦¿à¦¶à§‡à¦·',
                'ca': u'Especial',
                'cs': u'SpeciÃ¡lnÃ­',
                'csb': u'SpecjalnÃ´',
                'cy': u'Arbennig',
                'da': u'Speciel',
                'de': u'Spezial',
                'eo': u'Speciala',
                'es': u'Especial',
                'et': u'Eri',
                'fa': u'ÙˆÛŒÚ˜Ù‡',
                'fi': u'Toiminnot',
                'fy': u'Wiki',
                'ga': u'Speisialta',
                'he': u'×ž×™×•×—×“',
                'hi': u'à¤µà¤¿à¤¶à¥‡à¤·',
                'hu': u'SpeciÃ¡lis',
                'id': u'Istimewa',
                'it': u'Speciale',
                'ja': u'ç‰¹åˆ¥',
                'ko': u'íŠ¹ìˆ˜ê¸°ëŠ¥',
                'la': u'Specialis',
                'ms': u'Istimewa',
                'nb': u'Spesial',
                'nl': u'Speciaal',
                'no': u'Spesial',
                'oc': u'Especial',
                'pl': u'Specjalna',
                'pt': u'Especial',
                'ru': u'Ð¡Ð¿ÐµÑ†Ð¸Ð°Ð»ÑŒÐ½Ñ‹Ðµ',
                'sk': u'Å peciÃ¡lne',
                'sl': u'Posebno',
                'sq': u'Speciale',
                'sr': u'ÐŸÐ¾Ñ�ÐµÐ±Ð½Ð¾',
                'uk': u'Ð¡Ð¿ÐµÑ†Ñ–Ð°Ð»ÑŒÐ½Ñ–',
                'ta': u'à®šà®¿à®±à®ªà¯�à®ªà¯�',
                'th': u'à¸žà¸´à¹€à¸¨à¸©',
                'wa': u'SipeciÃ¥s',
            },
            0: {
                '_default': None,
            },
            1: {
                '_default': 'Talk',
                'de': u'Diskussion',
                'nl': u'Overleg',
                'pt': u'DiscussÃ£o'
            },
            2: {
                '_default': u'User',
                'de': u'Benutzer',
                'nl': u'Gebruiker',
                'pt': u'UsuÃ¡rio'
            },
            3: {
                '_default': u'User talk',
                'de': u'Benutzer Diskussion',
                'pt': u'UsuÃ¡rio DiscussÃ£o'
            },
            4: {
                '_default': u'Wikibooks'
            },
            5: {
                '_default': u'Wikibooks talk',
                'pt': u'Wikibooks DiscussÃ£o'
            },
            6: {
                # TODO: convert all percent-encoded titles to plaintext
                '_default': u'Image',
                'af': u'Beeld',
                'ar': u'ØµÙˆØ±Ø©',
                'bg': u'ÐšÐ°Ñ€Ñ‚Ð¸Ð½ÐºÐ°',
                #'bn': To be checked,
                'ca': u'Imatge',
                'cs': u'Soubor',
                'csb': u'Ã’brÃ´zk',
                'cy': u'Delwedd',
                'da': u'Billede',
                'de': u'Bild',
                'eo': u'Dosiero',
                'es': u'Imagen',
                'et': u'Pilt',
                'fa': u'ØªØµÙˆÛŒØ±',
                'fi': u'Kuva',
                'fr': u'Image',
                'fy': u'Ofbyld',
                'ga': u'Ã�omhÃ¡',
                'he': u'×ª×ž×•× ×”',
                'hi': u'à¤šà¤¿à¤¤à¥�à¤°',
                'hu': u'KÃ©p',
                'ia': u'Imagine',
                'id': u'Imej',
                'it': u'Immagine',
                'ja': u'ç”»åƒ�',
                'ko': u'ê·¸ë¦¼',
                'la': u'Imago',
                'ms': u'Imej',
                'nb': u'Bilde',
                'nl': u'Afbeelding',
                'no': u'Bilde',
                'oc': u'Image',
                'pl': u'Grafika',
                'pt': u'Imagem',
                'ro': u'Imagine',
                'ru': u'Ð˜Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ',
                'sk': u'ObrÃ¡zok',
                'sl': u'Slika',
                'sq': u'Figura',
                'sr': u'Ð¡Ð»Ð¸ÐºÐ°',
                'sv': u'Bild',
                'ta': u'à®ªà®Ÿà®¿à®®à®®à¯�',
                'th': u'à¸ à¸²à¸ž',
                'wa': u'ImÃ¥dje',
            },
            7: {
                '_default': u'Image talk',
                'de': u'Bild Diskussion',
                'pt': u'Imagem DiscussÃ£o'
            },
            8: {
                '_default': u'MediaWiki',
                'bg': u'ÐœÐµÐ´Ð¸Ñ�Ð£Ð¸ÐºÐ¸',
            },
            9: {
                '_default': u'MediaWiki talk',
                'de': u'MediaWiki Diskussion',
                'pt': u'MediaWiki DiscussÃ£o'
            },
            10: {
                '_default':u'Template',
                'de':u'Vorlage',
                'nl':u'Sjabloon',
                'pt':u'PredefiniÃ§Ã£o'
            },
            11: {
                '_default': u'Template talk',
                'de': u'Vorlage Diskussion',
                'pt': u'PredefiniÃ§Ã£o DiscussÃ£o'
            },
            12: {
                '_default': u'Help',
                'de': u'Hilfe',
                'pt': u'Ajuda',
            },
            13: {
                '_default': u'Help talk',
                'de': u'Hilfe Diskussion',
                'pt': u'Ajuda DiscussÃ£o',
            },
            14: {
                '_default': u'Category',
                'da': u'Kategori',
                'de': u'Kategorie',
                'es': u'CategorÃ­a',
                'fr': u'CatÃ©gorie',
                'hu': u'KategÃ³ria',
                'is': u'Flokkur',
                'nl': u'Categorie',
                'no': u'Kategori',
                'pt': u'Categoria',
                'sv': u'Kategori'
            },
            15: {
                '_default': u'Category talk',
                'de': u'Kategorie Diskussion',
                'pt': u'Categoria DiscussÃ£o'
            },
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
            'hu': ['en'],
            'pl': alphabetic,
            'simple': alphabetic
            }
        
        # group of languages that we might want to do at once
        
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
        
