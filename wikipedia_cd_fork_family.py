"""
# A fork of the German Wikipedia which will be used to create a 'stable' version
# which can be distributed on CDs.
"""

# -*- coding: utf-8  -*-

import urllib
import family, config

class Family(family.Family):
   
    def __init__(self):
        global langs
        self.langs = {
            'de':'cd.wikidev.net',   # German
            
            'af':'af.wikipedia.org',   # Afrikaans
            'als':'als.wikipedia.org', # Alsatian
            'ar':'ar.wikipedia.org',   # Arabic
            'ast':'ast.wikipedia.org', # Asturian
            'ay':'ay.wikipedia.org',   # Aymara
            'az':'az.wikipedia.org',   # Azerbaijan
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
            'minnan':'zh-min-nan.wikipedia.org', # Min-Nan
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
            'nn':'nn.wikipedia.org',   # Nynorsk
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
        
        self.obsolete = ['sh', 'dk', 'tlh']
        
        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wikimedia family.
        
        self.biglangs = ['da', 'de', 'en', 'es', 'fr', 'it', 'ja', 'nl', 'pl', 'sv']
        
        self.biglangs2 = self.biglangs + [
                    'ca', 'eo', 'et', 'fi', 'he', 'no', 'pt', 'ro', 'sl', 'zh']
        
        self.biglangs3 = self.biglangs2 + [
                    'af', 'bg', 'cs', 'cy', 'hr', 'hu', 'ia', 'id', 'la', 'ms',
                    'simple', 'wa']
        
        self.biglangs4 = self.biglangs3 + [
                        'ast', 'eu', 'fy', 'gl', 'io', 'is', 'ko', 'ku', 'lt', 'nds',
                        'oc', 'sk', 'sr', 'su', 'tr', 'ru', 'uk']
        
        self.seriouslangs = self.biglangs4 + [
                        'ar', 'be', 'bs', 'csb', 'el', 'fa', 'ga', 'hi', 'jv', 'lb', 'lv',
                        'mi', 'minnan', 'sa', 'ta', 'th', 'tokipona', 'tt', 'ur', 'vi']
        
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
        
    def put_address(self, code, name):
        return '/%s?action=submit' % name

    def get_address(self, code, name):
        return '/%s?redirect=no' % name 

    def references_address(self, code, name):
        return "/%s:Whatlinkshere?target=%s&limit=%d" % (self.special_namespace_url(code), name, config.special_page_limit)

    def upload_address(self, code):
        return '/%s:Upload' % self.special_namespace_url(code)

    def maintenance_address(self, code, maintenance_page, default_limit = True):
        if default_limit:
            return ('/%s:Maintenance?subfunction=' % self.special_namespace_url(code)) + maintenance_page
        else:
            return ('/%s:Maintenance?subfunction=' % self.special_namespace_url(code)) + maintenance_page + '&limit=' + str(config.special_page_limit)

    def allmessages_address(self, code):
        return ("/%s:Allmessages?ot=html" % self.special_namespace_url(code))

    def login_address(self, code):
        return ('/%s:Userlogin?action=submit' % self.special_namespace_url(code))

    def move_address(self, code):
        return ('/%s:Movepage?action=submit' % self.special_namespace_url(code))

    def delete_address(self, name):
        return '/%s?action=delete' % name

    def export_address(self, code):
        return '/%s:Export' % self.special_namespace_url(code)

    def allpagesname(self, code, start):
        # This is very ugly: to get all pages, the wikipedia code
        # 'fakes' getting a page with the returned name.
        # This will need to be fixed someday.
        if self.version(code)=="1.2":
            return '/%s:Allpages?printable=yes&from=%s' % (self.special_namespace_url(code), start)
        else:
            return '/%s:Allpages?from=%s' % (self.special_namespace_url(code), start)

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
