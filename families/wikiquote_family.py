# -*- coding: utf-8  -*-
import urllib
import family, config

# The wikimedia family that is known as Wikiquote

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikiquote'
        
        # Known wikiquote languages, given as a dictionary mapping the language code
        # to the hostname of the site hosting that wikiquote. For human consumption,
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
    
        # Most namespaces are inherited from family.Family()
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces[4] = {
            '_default': u'Wikiquote',
        },
        self.namespaces[5] = {
            '_default': u'Wikiquote talk',
            'pt': u'Wikiquote DiscussÃ£o',
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
            'he': ['en'],
            'hu': ['en'],
            'pl': alphabetic,
            'simple': alphabetic
            }
            
        # group of languages that we might want to do at once
            
        self.cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic
