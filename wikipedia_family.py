# The wikimedia family that is known as wikipedia, the encyclopedia

# Known wikipedia languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikipedia. For human consumption,
# the full name of the language is given behind each line as a comment

langs = {
    'af':'af.wikipedia.org',   # Afrikaans
    'als':'als.wikipedia.org', # Alsatian
    'ar':'ar.wikipedia.org',   # Arabic
    'az':'az.wikipedia.org',   # Azerbaijan
    'be':'be.wikipedia.org',   # Belorussian
    'bg':'bg.wikipedia.org',   # Bulgarian
    'bi':'bi.wikipedia.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
    'bn':'bn.wikipedia.org',   # Bengali
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
    'fr':'fr.wikipedia.org',   # French
    'fy':'fy.wikipedia.org',   # Frisian
    'ga':'ga.wikipedia.org',   # Irish Gaelic
    'gd':'gd.wikipedia.org',   # Scottish Gaelic
    'gl':'gl.wikipedia.org',   # Galician
    'gn':'gn.wikipedia.org',   # Guarani
    'gv':'gv.wikipedia.org',   # Manx
    'he':'he.wikipedia.org',   # Hebrew
    'hi':'hi.wikipedia.org',   # Hindi
    'hr':'hr.wikipedia.org',   # Croatian
    'hu':'hu.wikipedia.org',   # Hungarian
    'ia':'ia.wikipedia.org',   # Interlingua
    'id':'id.wikipedia.org',   # Indonesian
    'io':'io.wikipedia.org',   # Ido
    'is':'is.wikipedia.org',   # Icelandic
    'it':'it.wikipedia.org',   # Italian
    'ja':'ja.wikipedia.org',   # Japanese
    'jv':'jv.wikipedia.org',   # Javanese
    'ka':'ka.wikipedia.org',   # Georgian
    'ko':'ko.wikipedia.org',   # Korean
    'ks':'ks.wikipedia.org',   # Ekspreso, but should become Kashmiri
    'ku':'ku.wikipedia.org',   # Kurdish
    'la':'la.wikipedia.org',   # Latin
    'lt':'lt.wikipedia.org',   # Latvian
    'lv':'lv.wikipedia.org',   # Livonian
    'mg':'mg.wikipedia.org',   # Malagasy
    'mi':'mi.wikipedia.org',   # Maori
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
    'test':'test.wikipedia.org',
    'th':'th.wikipedia.org',   # Thai
    'tl':'tl.wikipedia.org',   # Tagalog
    'tlh':'tlh.wikipedia.org', # Klingon
    'tokipona':'tokipona.wikipedia.org', # Toki Pona
    'tpi':'tpi.wikipedia.org', # Tok Pisin
    'tr':'tr.wikipedia.org',   # Turkish
    'tt':'tt.wikipedia.org',   # Tatar
    'uk':'uk.wikipedia.org',   # Ukrainian
    'ur':'ur.wikipedia.org',   # Urdu
    'vi':'vi.wikipedia.org',   # Vietnamese
    'vo':'vo.wikipedia.org',   # Volapuk
    'wa':'wa.wikipedia.org',   # Walon
    'xh':'xh.wikipedia.org',   # isiXhosa
    'yi':'yi.wikipedia.org',   # Yiddish
    'yo':'yo.wikipedia.org',   # Yoruba
    'za':'za.wikipedia.org',   # Zhuang
    'zh':'zh.wikipedia.org',   # Chinese
    'zh-cfr':'zh-cfr.wikipedia.org', # Min-Nan
    'zh-cn':'zh.wikipedia.org', # Simplified Chinese
    'zh-tw':'zh.wikipedia.org', # Traditional Chinese
    }

# Translation used on all wikipedia's for the Special: namespace.
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

obsolete = ['sh', 'dk']

# A few selected big languages for things that we do not want to loop over
# all languages. This is only needed by the titletranslate.py module, so
# if you carefully avoid the options, you could get away without these
# for another wikimedia family.

biglangs = ['da', 'de', 'en', 'es', 'fr', 'ja', 'nl', 'pl', 'sv']

biglangs2 = biglangs + [
            'ca', 'eo', 'et', 'fi', 'he', 'it', 'no', 'pt', 'ro', 'sl',
            'zh']

biglangs3 = biglangs2 + [
            'af', 'cs', 'eu', 'gl', 'hr', 'ia', 'id', 'la', 'ms', 'ru',
            'simple']

seriouslangs  = biglangs3 + [
                'ar', 'bg', 'bs', 'cy', 'el', 'fa', 'fy', 'hi', 'hu', 'ko',
                'is', 'ku', 'lt', 'nds', 'oc', 'sr', 'ta', 'th', 'tr', 'uk',
                'ur', 'vi']

# other groups of language that we might want to do at once

cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic


#
# Some functionality that is simple for the wikipedia family, but more
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
    # This is very ugly: to get all pages, the wikipedia code
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
latin1 = ['en', 'sv', 'nl', 'de', 'es', 'da', 'dk', 'test']

# Languages that used to be coded in iso-8859-1
latin1old = ['et', 'ia', 'la', 'af', 'cs', 'fr', 'pt', 'sl', 'bs', 'fy',
             'vi', 'lt', 'fi', 'it', 'no', 'simple', 'gl', 'eu',
             'nds', 'co', 'mr', 'id', 'lv', 'sw', 'tt', 'uk', 'vo',
             'ga', 'na']

            
def code2encoding(code):
    """Return the encoding for a specific language wikipedia"""
    if code == 'ascii':
        return code # Special case where we do not want special characters.
    if code in latin1:
        return 'iso-8859-1'
    return 'utf-8'

def code2encodings(code):
    """Return a list of historical encodings for a specific language
       wikipedia"""
    # Historic compatibility
    if code == 'pl':
        return 'utf-8', 'iso-8859-2'
    if code == 'ru':
        return 'utf-8', 'iso-8859-5'
    if code in latin1old:
        return 'utf-8', 'iso-8859-1'
    return code2encoding(code),
