# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as wiktionary

# Known wiktionary languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wiktionary. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):
    name = 'wiktionary'

    langs = {
        'aa':'aa.wiktionary.org',   # Afar
        'af':'af.wiktionary.org',   # Afrikaans
        'als':'als.wiktionary.org', # Alsatian
        'an':'an.wiktionary.org',   # Aragonese
        'ang':'ang.wiktionary.org', # Anglo-Saxon
        'ar':'ar.wiktionary.org',   # Arabic
        'as':'as.wiktionary.org',   # Assamese
        'ast':'ast.wiktionary.org', # Asturian
        'ay':'ay.wiktionary.org',   # Aymara
        'az':'az.wiktionary.org',   # Azerbaijan
        'be':'be.wiktionary.org',   # Belorussian
        'bg':'bg.wiktionary.org',   # Bulgarian
        'bh':'bh.wiktionary.org',   # Bhojpuri
        'bi':'bi.wiktionary.org',   # Bislama
        'bn':'bn.wiktionary.org',   # Bengali
        'bo':'bo.wiktionary.org',   # Tibetan
        'br':'br.wiktionary.org',   # Breton
        'bs':'bs.wiktionary.org',   # Bosnian
        'ca':'ca.wiktionary.org',   # Catalan
        'chr':'chr.wiktionary.org', # Cherokee
        'co':'co.wiktionary.org',   # Corsican
        'cs':'cs.wiktionary.org',   # Czech
        'csb':'csb.wiktionary.org', # Kashubian
        'cy':'cy.wiktionary.org',   # Welsh
        'da':'da.wiktionary.org',   # Danish
        'de':'de.wiktionary.org',   # German
        'ee':'ee.wiktionary.org',   # Ewe
        'el':'el.wiktionary.org',   # Greek
        'en':'en.wiktionary.org',   # English
        'eo':'eo.wiktionary.org',   # Esperanto
        'es':'es.wiktionary.org',   # Spanish
        'et':'et.wiktionary.org',   # Estonian
        'eu':'eu.wiktionary.org',   # Basque
        'fa':'fa.wiktionary.org',   # Farsi
        'fi':'fi.wiktionary.org',   # Finnish
        'fo':'fo.wiktionary.org',   # Faroese
        'fr':'fr.wiktionary.org',   # French
        'fy':'fy.wiktionary.org',   # Frisian
        'ga':'ga.wiktionary.org',   # Irish Gaelic
        'gd':'gd.wiktionary.org',   # Scottish Gaelic
        'gl':'gl.wiktionary.org',   # Galician
        'gn':'gn.wiktionary.org',   # Guarani
        'gu':'gu.wiktionary.org',   # Gujarati
        'gv':'gv.wiktionary.org',   # Manx
        'ha':'ha.wiktionary.org',   # Hausa
        'he':'he.wiktionary.org',   # Hebrew
        'hi':'hi.wiktionary.org',   # Hindi
        'hr':'hr.wiktionary.org',   # Croatian
        'hu':'hu.wiktionary.org',   # Hungarian
        'hy':'hy.wiktionary.org',   # Armenian
        'ia':'ia.wiktionary.org',   # Interlingua
        'id':'id.wiktionary.org',   # Indonesian
        'ie':'ie.wiktionary.org',   # Interlingue
        'io':'io.wiktionary.org',   # Ido
        'is':'is.wiktionary.org',   # Icelandic
        'it':'it.wiktionary.org',   # Italian
        'ja':'ja.wiktionary.org',   # Japanese
        'jbo':'jbo.wiktionary.org', # Lojban
        'jv':'jv.wiktionary.org',   # Javanese
        'ka':'ka.wiktionary.org',   # Georgian
        'kk':'kk.wiktionary.org',   # Kazakh
        'km':'km.wiktionary.org',   # Khmer
        'kn':'kn.wiktionary.org',   # Kannada
        'ko':'ko.wiktionary.org',   # Korean
        'ks':'ks.wiktionary.org',   # Ekspreso, but should become Kashmiri
        'ku':'ku.wiktionary.org',   # Kurdish
        'kw':'kw.wiktionary.org',   # Cornish
        'ky':'ky.wiktionary.org',   # Kirghiz
        'la':'la.wiktionary.org',   # Latin
        'lb':'lb.wiktionary.org',   # Luxembourgish
        'ln':'ln.wiktionary.org',   # Lingala
        'lo':'lo.wiktionary.org',   # Lao
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
        'mt':'mt.wiktionary.org',   # Maltese
        'my':'my.wiktionary.org',   # Burmese
        'na':'na.wiktionary.org',   # Nauruan
        'nah':'nah.wiktionary.org', # Nahuatl
        'nb':'no.wiktionary.org',   # Norse - new code for Bokmal to distinguish from Nynorsk
        'nds':'nds.wiktionary.org', # Lower Saxon
        'ne':'ne.wiktionary.org',   # Nepalese
        'nl':'nl.wiktionary.org',   # Dutch
        'nn':'nn.wiktionary.org',   # Nynorsk
        'no':'no.wiktionary.org',   # Norwegian
        'nv':'nv.wiktionary.org',   # Navajo
        'oc':'oc.wiktionary.org',   # Occitan
        'om':'om.wiktionary.org',   # Oromo
        'pa':'pa.wiktionary.org',   # Punjabi
        'pi':'pi.wiktionary.org',   # Pali
        'pl':'pl.wiktionary.org',   # Polish
        'ps':'ps.wiktionary.org',   # Pashto (Afghan)
        'pt':'pt.wiktionary.org',   # Portuguese
        'qu':'qu.wiktionary.org',   # Quechua
        'rm':'rm.wiktionary.org',   # Romansch
        'ro':'ro.wiktionary.org',   # Romanian
        'roa-rup':'roa-rup.wiktionary.org', # Aromanian
        'ru':'ru.wiktionary.org',   # Russian
        'sa':'sa.wiktionary.org',   # Sanskrit
        'scn':'scn.wiktionary.org', # Sicilian
        'sd':'sd.wiktionary.org',   # Sindhi
        'se':'se.wiktionary.org',   # Saami
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
        'te':'te.wikitonary.org',   # Telugu
        'test':'test.wikipedia.org.',
        'tg':'tg.wiktionary.org',   # Tajik
        'th':'th.wiktionary.org',   # Thai
        'tk':'tk.wiktionary.org',   # Turkmen
        'tl':'tl.wiktionary.org',   # Tagalog
        'tlh':'tlh.wiktionary.org', # Klingon
        'tn':'tn.wiktionary.org',   # Tswana
        'to':'to.wiktionary.org',   # Tongan
        'tokipona':'tokipona.wiktionary.org', # Toki Pona
        'tpi':'tpi.wiktionary.org', # Tok Pisin
        'tr':'tr.wiktionary.org',   # Turkish
        'tt':'tt.wiktionary.org',   # Tatar
        'ug':'ug.wiktionary.org',   # Uyghur
        'uk':'uk.wiktionary.org',   # Ukrainian
        'ur':'ur.wiktionary.org',   # Urdu
        'uz':'uz.wiktionary.org',   # Uzbek
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
        'zu':'zu.wikipedia.org',    # Zulu
        }
    

    # On most Wikipedias page names must start with a capital letter, but some
    # languages don't use this.
        
    nocapitalize = ['cs', 'de', 'es', 'fr', 'gu', 'hi', 'it', 'kn', 'ku',
                    'nl', 'sq', 'sv', 'tlh','tokipona', 'tr']

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


    interwiki_putfirst = {
        'en': self.alphabetic,
        'fr': self.alphabetic,
        'hu': ['en'],
        'pl': self.alphabetic,
        'simple': self.alphabetic
        }
        
    # group of languages that we might want to do at once
    
    cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
       
    # Function to figure out the encoding of different languages
    # Languages that are coded in iso-8859-1
    latin1 = []
    
    def code2encoding(self, code):
        """Return the encoding for a specific language wiktionary"""
        if code in self.latin1:
            return 'iso-8859-1'
        return 'utf-8'
    
