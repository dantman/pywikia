# -*- coding: utf-8  -*-
import urllib
import family, config

# The wikimedia family that is known as Wikibooks

class Family(family.Family):

    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikibooks'
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

        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': u'Wikibooks',
        },
        self.namespaces[5] = {
            '_default': u'Wikibooks talk',
            'pt': u'Wikibooks DiscussÃ£o',
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
        
