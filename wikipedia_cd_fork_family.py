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
                'de': u'Spezial',
            },
            0: {
                '_default': None,
            },
            1: {
                '_default': 'Talk',
                'de': u'Diskussion',
            },
            2: {
                '_default': u'User',
                'de': u'Benutzer',
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
                '_default': u'Image',
                'de': u'Bild',
            },
            7: {
                '_default': u'Image talk',
                'de': u'Bild Diskussion',        
            },
            8: {
                '_default': u'MediaWiki',
            },
            9: {
                '_default': u'MediaWiki talk',
                'de': u'MediaWiki Diskussion',
            },
            10: {
                '_default':u'Template',
                'de':u'Vorlage',
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
           },
            15: {
                '_default': u'Category talk',
                'de': u'Kategorie Diskussion',        
            },
        }
        
        self.obsolete = ['sh', 'dk']
        
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

