# The wikimedia family that is known as wiktionary

# Known wiktionary languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wiktionary. For human consumption,
# the full name of the language is given behind each line as a comment

langs = {
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

# Translation used on all wiktionary's for the Special: namespace.
# Only necessary when it is not 'Special'.
special = {
    'af': 'Spesiaal',
    'ar': '%D8%AE%D8%A7%D8%B5',
    'bg': '%D0%A1%D0%BF%D0%B5%D1%86%D0%B8%D0%B0%D0%BB%D0%BD%D0%B8',
    'bn': '%E0%A6%AC%E0%A6%BF%E0%A6%B6%E0%A7%87%E0%A6%B7',
    'ca': 'Especial',
    'cs': 'Speci%C3%A1ln%C3%AD',
    'csb': 'Specjaln%C3%B4',
    'cy': 'Arbennig',
    'da': 'Speciel',
    'de': 'Spezial',
    'en': 'Special',
    'eo': 'Speciala',
    'es': 'Especial',
    'et': 'Eri',
    'fa': '%D9%88%DB%8C%DA%98%D9%87',
    'fi': 'Toiminnot',
    'fr': 'Special',
    'fy': 'Wiki',
    'ga': 'Speisialta',
    'he': '%D7%9E%D7%99%D7%95%D7%97%D7%93',
    'hi': '%E0%A4%B5%E0%A4%BF%E0%A4%B6%E0%A5%87%E0%A4%B7',
    'hu': 'Speci%C3%A1lis',
    'ia': 'Special',
    'id': 'Istimewa',
    'it': 'Speciale',
    'ja': '%E7%89%B9%E5%88%A5',
    'ko': '%ED%8A%B9%EC%88%98%EA%B8%B0%EB%8A%A5',
    'la': 'Specialis',
    'ms': 'Istimewa',
    'nb': 'Spesial',
    'nl': 'Speciaal',
    'no': 'Spesial',
    'oc': 'Especial',
    'pl': 'Specjalna',
    'pt': 'Especial',
    'ro': 'Special',
    'ru': '%D0%A1%D0%BF%D0%B5%D1%86%D0%B8%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5',
    'sk': '%C5%A0peci%C3%A1lne',
    'sl': 'Posebno',
    'sq': 'Special',
    'sr': '%D0%9F%D0%BE%D1%81%D0%B5%D0%B1%D0%BD%D0%BE',
    'sv': 'Special',
    'ta': '%E0%AE%9A%E0%AE%BF%E0%AE%B1%E0%AE%AA%E0%AF%8D%E0%AE%AA%E0%AF%81',
    'th': '%E0%B8%9E%E0%B8%B4%E0%B9%80%E0%B8%A8%E0%B8%A9',
    'wa': 'Sipeci%C3%A5s',
    }

# And the image namespace.

image = {
    'af': 'Beeld',
    'ar': '%D8%B5%D9%88%D8%B1%D8%A9',
    'bg': '%D0%9A%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B0',
    #'bn': To be checked,
    'ca': 'Imatge',
    'cs': 'Soubor',
    'csb': 'Mal%C3%ABnk',
    'cy': 'Delwedd',
    'da': 'Billede',
    'de': 'Bild',
    'en': 'Image',
    'eo': 'Dosiero',
    'es': 'Imagen',
    'et': 'Pilt',
    'fa': '%D8%AA%D8%B5%D9%88%DB%8C%D8%B1',
    'fi': 'Kuva',
    'fr': 'Image',
    'fy': 'Ofbyld',
    'ga': '%C3%8Domh%C3%A1',
    'he': '%D7%AA%D7%9E%D7%95%D7%A0%D7%94',
    'hi': '%E0%A4%9A%E0%A4%BF%E0%A4%A4%E0%A5%8D%E0%A4%B0',
    'hu': 'K%C3%A9p',
    'ia': 'Imagine',
    'id': 'Imej',
    'it': 'Immagine',
    'ja': '%E7%94%BB%E5%83%8F',
    'ko': '%EA%B7%B8%EB%A6%BC',
    'la': 'Imago',
    'ms': 'Imej',
    'nb': 'Bilde',
    'nl': 'Afbeelding',
    'no': 'Bilde',
    'oc': 'Image',
    'pl': 'Grafika',
    'pt': 'Imagem',
    'ro': 'Imagine',
    'ru': '%D0%98%D0%B7%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5',
    'sk': 'Obr%C3%A1zok',
    'sl': 'Slika',
    'sq': 'Figura',
    'sr': '%D0%A1%D0%BB%D0%B8%D0%BA%D0%B0',
    'sv': 'Bild',
    'ta': '%E0%AE%AA%E0%AE%9F%E0%AE%BF%E0%AE%AE%E0%AE%AE%E0%AF%8D',
    'th': '%E0%B8%A0%E0%B8%B2%E0%B8%9E',
    'wa': 'Im%C3%A5dje',
    }

# Category namespace. 'Category' works on all languages?!?!?....

category = {
    'da': u'Kategori',
    'de': u'Kategorie',
    'en': u'Category',
    'nl': u'Categorie',
    'no': u'Kategori',
    'fr': u'Cat\xe9gorie',
    'sv': u'Kategori'
}

def category_namespaces(code):
    ns = []
    ns.append(category[code])
    ns.append(category[code].lower())
    ns.append(category['en'])
    ns.append(category['en'].lower())
    return ns

# Redirect code can be translated, but is only in one language now.

redirect = {
    'cy': 'ail-cyfeirio',
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

interwiki_putfirst = {
    'en': alphabetic,
    'fr': alphabetic,
    'hu': ['en'],
    'pl': alphabetic,
    'simple': alphabetic
    }

# Defaults for Special: and Image: namespace names

for lang in langs:
    if not lang in special:
        special[lang] = 'Special'
    if not lang in image:
        image[lang] = 'Image'

obsolete = []

# A few selected big languages for things that we do not want to loop over
# all languages. This is only needed by the titletranslate.py module, so
# if you carefully avoid the options, you could get away without these
# for another wikimedia family.

biglangs = ['de', 'en', 'eo', 'es', 'fi', 'fr', 'hu', 'ja', 'nl', 'pl',
            'ro', 'sv']

biglangs2 = biglangs + [
            'ca', 'et', 'eu', 'it', 'ko', 'ru', 'zh'
            ]

biglangs3 = biglangs2 + [
            'ar', 'bg', 'da', 'ia', 'tr', 'vi'
            ]

biglangs4 = biglangs3

seriouslangs = biglangs4

# other groups of language that we might want to do at once

cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic


#
# Some functionality that is simple for the wiktionary family, but more
# difficult for e.g. wikitravel
#

def hostname(code):
    return langs[code]

# Which version of MediaWiki is used?
def version(code):
    return "1.3"

def put_address(code, name):
    return '/w/wiki.phtml?title=%s&action=submit'%name

def get_address(code, name):
    return '/w/wiki.phtml?title='+name+"&redirect=no"

def references_address(code, name):
    return "/w/wiki.phtml?title=%s:Whatlinkshere&target=%s"%(special[code], name)

def upload_address(code):
    return '/wiki/%s:Upload'%special[code]

def login_address(code):
    return '/w/wiki.phtml?title=%s:Userlogin&amp;action=submit'%special[code]

def move_address(code):
    return '/w/wiki.phtml?title=%s:Movepage&action=submit'%special[code]

def export_address(code):
    return '/wiki/%s:Export'%special[code]

def allpagesname(code, start):
    # This is very ugly: to get all pages, the wiktionary code
    # 'fakes' getting a page with the returned name.
    # This will need to be fixed someday.
    if version(code)=="1.2":
        return '%s:Allpages&printable=yes&from=%s'%(special[code], start)
    else:
        return '%s:Allpages&from=%s'%(special[code], start)

#
# Two functions to figure out the encoding of different languages
# This may be a lot simpler for other families!
# 

# Languages that are coded in iso-8859-1
latin1 = []

# Languages that used to be coded in iso-8859-1
latin1old = []

            
def code2encoding(code):
    """Return the encoding for a specific language wiktionary"""
    if code == 'ascii':
        return code # Special case where we do not want special characters.
    if code in latin1:
        return 'iso-8859-1'
    return 'utf-8'

def code2encodings(code):
    """Return a list of historical encodings for a specific language
       wiktionary"""
    return code2encoding(code),
