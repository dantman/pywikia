import config

# The wikimedia family that is known as wikiquote, the encyclopedia

# Known wikiquote languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikiquote. For human consumption,
# the full name of the language is given behind each line as a comment

langs = {
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

# Translation used on all wikiquote's for the Special: namespace.
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

# Template namespace
template = {
    'de':u'Vorlage',
    'en':u'Template'
    }

# Category namespace. 'Category' works on all languages?!?!?....

category = {
    'da': u'Kategori',
    'de': u'Kategorie',
    'en': u'Category',
    'nl': u'Categorie',
    'no': u'Kategori',
    'fr': u'Cat\xe9gorie',
    'ru': u'Category',
    'sv': u'Kategori',
    'test': u'Category'
}

def category_namespaces(code):
    ns = []
    ns.append(category[code])
    ns.append(category[code].lower())
    if code!='en' and category[code] != category['en']:
    	ns.append(category['en'])
    	ns.append(category['en'].lower())
    return ns

# Redirect code can be translated, but is only in one language now.

redirect = {
    'cy': 'ail-cyfeirio',
    }

# On most Wikipedias page names must start with a capital letter, but some
# languages don't use this.

nocapitalize = ['tokipona']

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

biglangs = ['de', 'en', 'es', 'fr', 'ja', 'nl', 'pl', 'sv']

biglangs2 = biglangs + [
            'ca', 'da', 'eo', 'et', 'fi', 'he', 'it', 'no', 'pt', 'ro',
            'sl', 'zh']

biglangs3 = biglangs2 + [
            'af', 'bg', 'cs', 'cy', 'hr', 'ia', 'id', 'la', 'ms', 'simple',
            'wa']

biglangs4 = biglangs3 + [
                'ar', 'bs', 'el', 'eu', 'fy', 'gl', 'hu', 'is', 'ko', 'ku',
                'lt', 'nds', 'oc', 'ru', 'sr', 'tr', 'uk']

seriouslangs = biglangs4 + [
                'fa', 'hi', 'lv', 'ta', 'th', 'tt', 'ur', 'vi']

# other groups of language that we might want to do at once

cyrilliclangs = ['be', 'bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic


#
# Some functionality that is simple for the wikiquote family, but more
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
    return "/w/wiki.phtml?title=%s:Whatlinkshere&target=%s&limit=%d"%(special[code], name, config.special_page_limit)

def upload_address(code):
    return '/wiki/%s:Upload'%special[code]

def maintenance_address(code, maintenance_page, default_limit = True):
    if default_limit:
        return ('/w/wiki.phtml?title=%s:Maintenance&subfunction=' % special[code]) + maintenance_page
    else:
        return ('/w/wiki.phtml?title=%s:Maintenance&subfunction=' % special[code]) + maintenance_page + '&limit=' + str(config.special_page_limit)

def allmessages_address(code):
    return "/w/wiki.phtml?title=%s:Allmessages&ot=html" % special[code]
                        
def login_address(code):
    return '/w/wiki.phtml?title=%s:Userlogin&amp;action=submit'%special[code]

def move_address(code):
    return '/w/wiki.phtml?title=%s:Movepage&action=submit'%special[code]

def delete_address(name):
    return '/w/wiki.phtml?title=%s&action=delete' % name

def export_address(code):
    return '/wiki/%s:Export'%special[code]

def allpagesname(code, start):
    # This is very ugly: to get all pages, the wikiquote code
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
            
def code2encoding(code):
    """Return the encoding for a specific language wikiquote"""
    return 'utf-8'

def code2encodings(code):
    return code2encoding(code),
