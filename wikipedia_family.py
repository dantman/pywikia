# -*- coding: utf-8  -*-

import urllib
import family, config

# The Wikimedia family that is known as Wikipedia, the Free Encyclopedia

class Family(family.Family):
    # Known wikipedia languages, given as a dictionary mapping the language code
    # to the hostname of the site hosting that wikipedia. For human consumption,
    # the full name of the language is given behind each line as a comment
    
    def __init__(self):
        global langs
        self.langs = {
            'af':'af.wikipedia.org',   # Afrikaans
            'als':'als.wikipedia.org', # Alsatian
            'ar':'ar.wikipedia.org',   # Arabic
            'ay':'ay.wikipedia.org',   # Aymara            'az':'az.wikipedia.org',   # Azerbaijan
            'be':'be.wikipedia.org',   # Belorussian
            'bg':'bg.wikipedia.org',   # Bulgarian
            'bh':'bh.wikipedia.org',   # Bhojpuri
            'bi':'bi.wikipedia.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
            'bn':'bn.wikipedia.org',   # Bengali
            'br':'br.wikipedia.org',   # Breton
            'bs':'bs.wikipedia.org',   # Bosnian
            'ca':'ca.wikipedia.org',   # Catalan
            'chr':'chr.wikipedia.org', # Cherokee
            'co':'co.wikipedia.org',   # Corsican
            'cs':'cs.wikipedia.org',   # Czech
            'csb':'csb.wikipedia.org', # Kashubian
            'cy':'cy.wikipedia.org',   # Welsh
            'da':'da.wikipedia.org',   # Danish
            'de':'de.wikipedia.org',   # German
            'dk':'da.wikipedia.org',   # Danish (wrong name)
            'el':'el.wikipedia.org',   # Greek
            'en':'en.wikipedia.org',   # English
            'eo':'eo.wikipedia.org',   # Esperanto
            'es':'es.wikipedia.org',   # Spanish
            'et':'et.wikipedia.org',   # Estonian
            'eu':'eu.wikipedia.org',   # Basque
            'fa':'fa.wikipedia.org',   # Farsi
            'fi':'fi.wikipedia.org',   # Finnish
            'fo':'fo.wikipedia.org',   # Faroese
            'fr':'fr.wikipedia.org',   # French
            'fy':'fy.wikipedia.org',   # Frisian
            'ga':'ga.wikipedia.org',   # Irish Gaelic
            'gd':'gd.wikipedia.org',   # Scottish Gaelic
            'gl':'gl.wikipedia.org',   # Galician
            'gn':'gn.wikipedia.org',   # Guarani
            'gu':'gu.wikipedia.org',   # Gujarati
            'gv':'gv.wikipedia.org',   # Manx
            'ha':'ha.wikipedia.org',   # Hausa
            'he':'he.wikipedia.org',   # Hebrew
            'hi':'hi.wikipedia.org',   # Hindi
            'hr':'hr.wikipedia.org',   # Croatian
            'hu':'hu.wikipedia.org',   # Hungarian
            'ia':'ia.wikipedia.org',   # Interlingua
            'id':'id.wikipedia.org',   # Indonesian
            'ie':'ie.wikipedia.org',   # Interlingue
            'io':'io.wikipedia.org',   # Ido
            'is':'is.wikipedia.org',   # Icelandic
            'it':'it.wikipedia.org',   # Italian
            'ja':'ja.wikipedia.org',   # Japanese
            'jbo':'jbo.wikipedia.org', # Lojban
            'jv':'jv.wikipedia.org',   # Javanese
            'ka':'ka.wikipedia.org',   # Georgian
            'km':'km.wikipedia.org',   # Khmer
            'kn':'kn.wikipedia.org',   # Kannada
            'ko':'ko.wikipedia.org',   # Korean
            'ks':'ks.wikipedia.org',   # Ekspreso, but should become Kashmiri
            'ku':'ku.wikipedia.org',   # Kurdish
            'kw':'kw.wikipedia.org',   # Cornish
            'ky':'ky.wikipedia.org',   # Kirghiz
            'la':'la.wikipedia.org',   # Latin
            'lb':'lb.wikipedia.org',   # Luxembourgish
            'lt':'lt.wikipedia.org',   # Latvian
            'lv':'lv.wikipedia.org',   # Livonian
            'mg':'mg.wikipedia.org',   # Malagasy
            'mi':'mi.wikipedia.org',   # Maori
            'minnan':'minnan.wikipedia.org', # Min-Nan
            'mk':'mk.wikipedia.org',   # Macedonian
            'ml':'ml.wikipedia.org',   # Malayalam
            'mn':'mn.wikipedia.org',   # Mongolian
            'mr':'mr.wikipedia.org',   # Marathi
            'ms':'ms.wikipedia.org',   # Malay
            'na':'na.wikipedia.org',   # Nauruan
            'nah':'nah.wikipedia.org', # Nahuatl
            'nb':'no.wikipedia.org',   # Norse - new code for Bokmal to distinguish from Nynorsk
            'nds':'nds.wikipedia.org', # Lower Saxon
            'nl':'nl.wikipedia.org',   # Dutch
            'no':'no.wikipedia.org',   # Norwegian
            'oc':'oc.wikipedia.org',   # Occitan
            'om':'om.wikipedia.org',   # Oromo
            'pl':'pl.wikipedia.org',   # Polish
            'pt':'pt.wikipedia.org',   # Portuguese
            'qu':'qu.wikipedia.org',   # Quechua
            'rm':'rm.wikipedia.org',   # Romansch
            'ro':'ro.wikipedia.org',   # Romanian
            'roa-rup':'roa-rup.wikipedia.org', # Aromanian
            'ru':'ru.wikipedia.org',   # Russian
            'sa':'sa.wikipedia.org',   # Sanskrit
            'sh':'sh.wikipedia.org',   # OBSOLETE, Serbocroatian
            'si':'si.wikipedia.org',   # Sinhalese
            'simple':'simple.wikipedia.org', # Simple English
            'sk':'sk.wikipedia.org',   # Slovakian
            'sl':'sl.wikipedia.org',   # Slovenian
            'sq':'sq.wikipedia.org',   # Albanian
            'sr':'sr.wikipedia.org',   # Serbian
            'st':'st.wikipedia.org',   # Sesotho
            'su':'su.wikipedia.org',   # Sundanese
            'sv':'sv.wikipedia.org',   # Swedish
            'sw':'sw.wikipedia.org',   # Swahili
            'ta':'ta.wikipedia.org',   # Tamil
            'te':'te.wikipedia.org',   # Telugu
            'test':'test.wikipedia.org',
            'th':'th.wikipedia.org',   # Thai
            'tk':'tk.wikipedia.org',   # Turkmen
            'tl':'tl.wikipedia.org',   # Tagalog
            'tlh':'tlh.wikipedia.org', # Klingon
            'tn':'tn.wikipedia.org',   # Tswana
            'tokipona':'tokipona.wikipedia.org', # Toki Pona
            'tpi':'tpi.wikipedia.org', # Tok Pisin
            'tr':'tr.wikipedia.org',   # Turkish
            'tt':'tt.wikipedia.org',   # Tatar
            'ug':'ug.wikipedia.org',   # Uyghur
            'uk':'uk.wikipedia.org',   # Ukrainian
            'ur':'ur.wikipedia.org',   # Urdu
            'uz':'uz.wikipedia.org',   # Uzbek
            'vi':'vi.wikipedia.org',   # Vietnamese
            'vo':'vo.wikipedia.org',   # Volapuk
            'wa':'wa.wikipedia.org',   # Walon
            'xh':'xh.wikipedia.org',   # isiXhosa
            'yi':'yi.wikipedia.org',   # Yiddish
            'yo':'yo.wikipedia.org',   # Yoruba
            'za':'za.wikipedia.org',   # Zhuang
            'zh':'zh.wikipedia.org',   # Chinese
            'zh-cn':'zh.wikipedia.org', # Simplified Chinese
            'zh-tw':'zh.wikipedia.org', # Traditional Chinese
            'zu':'zu.wikipedia.org',   # Zulu
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
                '_default': u'Wikipedia',
            },
            5: {
                '_default': u'Wikipedia talk',
                'de': u'Wikipedia Diskussion',
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
                'es':u'Plantilla',
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
        
        
        # Redirect code can be translated, but is only in one language now.
        
        self.redirect = {
            'cy': 'ail-cyfeirio',
            }
        
        # On most Wikipedias page names must start with a capital letter, but some
        # languages don't use this.
        
        self.nocapitalize = ['tlh','tokipona']
        
        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.

rm tk ug 

        self.alphabetic = ['af','ar','roa-rup','ay','bg','be','bn','bs','br',
                      'ca','chr','co','cs','cy','da','de','als','et',
                      'el','en','es','eo','eu','fa','fr','fy','ga','gv',
                      'gd','gl','ko','ha','hi','hr','io','id','ia','is','it',
                      'he','jv','kn','ka','csb','ks','kw','ky','sw','la','lv',
                      'lt','jbo','hu','mk','mg','ml','mi','mr','ms','minnan',
                      'mn','nah','na','nl','ja','no','nb','oc','om','ug','nds',
                      'pl','pt','ro','rm','qu','ru','sa','st','sq','si','simple',
                      'sk','sl','sr','su','fi','sv','ta','tt','th','tlh','tk',
                      'tw','vi','tokipona','tpi','tr','ur','uk','vo','wa','yi',
                      'yo','za','zh','zh-cn','zh-tw']
        
        self.interwiki_putfirst = {
            'en': self.alphabetic,
            'fr': self.alphabetic,
            'hu': ['en'],
            'pl': self.alphabetic,
            'simple': self.alphabetic,
            'fi': ['ab','aa','af','am','ar','an','roa-rup','as','ast','gn','ay',
                   'az','id','jv','ms','su','ban','bal','bn','ba','be','mr','bh',
                   'bi','bo','nb','bs','br','bug','bg','ca','chr','cs','ch','che',
                   'sn','co','za','cy','da','de','di','dz','et','el','en','als',
                   'es','eo','eu','fa','fo','fr','fy','ga','gv','sm','gd','gl',
                   'gay','gu','ko','ha','hy','hi','hr','iba','io','ia','iu','ik',
                   'xh','zu','is','it','he','kl','kn','ka','csb','ks','kaw','kw',
                   'kk','rw','ky','rn','sw','ku','la','ls','lv','lt','li','ln',
                   'jbo','mad','hu','mak','mk','ml','mg','mt','mi','min','minnan',
                   'mo','mn','my','nah','na','fj','ng','nl','ne','ja','no','nn',
                   'oc','or','om','ug','pa','ps','km','lo','nds','pl','pt','ro',
                   'rm','qu','ru','sa','sg','st','tn','sq','si','simple','sd','ss',
                   'sk','sl','sr','fi','sv','tl','ta','tt','te','th','ti','tlh',
                   'vi','tg','tokipona','tpi','to','tr','tk','tw','ur','uk','uz',
                   'vo','wa','wo','ts','yi','yo','zh','zh-tw','zh-cn']
            }
        
        # Defaults for Special: and Image: namespace names
        
        #for lang in langs:
        #    if not lang in special:
        #        special[lang] = 'Special'
        #    if not lang in image:
        #        image[lang] = 'Image'
        
        self.obsolete = ['sh', 'dk']
        
        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wikimedia family.
        
        self.biglangs = ['de', 'en', 'es', 'fr', 'ja', 'nl', 'pl', 'sv']
        
        self.biglangs2 = self.biglangs + [
                    'ca', 'da', 'eo', 'et', 'fi', 'he', 'it', 'no', 'pt', 'ro',
                    'sl', 'zh']
        
        self.biglangs3 = self.biglangs2 + [
                    'af', 'bg', 'cs', 'cy', 'hr', 'ia', 'id', 'la', 'ms', 'simple',
                    'wa']
        
        self.biglangs4 = self.biglangs3 + [
                        'ar', 'bs', 'el', 'eu', 'fy', 'gl', 'hu', 'is', 'ko', 'ku',
                        'lt', 'nds', 'oc', 'ru', 'sr', 'tr', 'uk']
        
        self.seriouslangs = self.biglangs4 + [
                        'fa', 'hi', 'lv', 'ta', 'th', 'tt', 'ur', 'vi']
        
        # other groups of language that we might want to do at once
        
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
        
        
        #
        # Two functions to figure out the encoding of different languages
        # This may be a lot simpler for other families!
        # 
        
        # Languages that are coded in iso-8859-1
        self.latin1 = ['en', 'sv', 'nl', 'da', 'dk', 'test']
        
        # Languages that used to be coded in iso-8859-1
        self.latin1old = ['de', 'et', 'es', 'ia', 'la', 'af', 'cs', 'fr', 'pt', 'sl', 'bs', 'fy',
                     'vi', 'lt', 'fi', 'it', 'no', 'simple', 'gl', 'eu',
                     'nds', 'co', 'mr', 'id', 'lv', 'sw', 'tt', 'uk', 'vo',
                     'ga', 'na', 'es']
        
                
    def code2encoding(self, code):
        """Return the encoding for a specific language wikipedia"""
        if code in self.latin1:
            return 'iso-8859-1'
        return 'utf-8'
    
    def code2encodings(self, code):
        """Return a list of historical encodings for a specific language
           wikipedia"""
        # Historic compatibility
        if code == 'pl':
            return 'utf-8', 'iso-8859-2'
        if code == 'ru':
            return 'utf-8', 'iso-8859-5'
        if code in self.latin1old:
            return 'utf-8', 'iso-8859-1'
        return self.code2encoding(code),
