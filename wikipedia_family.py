# -*- coding: utf-8  -*-

import config, urllib

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
    'io':'io.wikipedia.org',   # Ido
    'is':'is.wikipedia.org',   # Icelandic
    'it':'it.wikipedia.org',   # Italian
    'ja':'ja.wikipedia.org',   # Japanese
    'jv':'jv.wikipedia.org',   # Javanese
    'ka':'ka.wikipedia.org',   # Georgian
    'km':'km.wikipedia.org',   # Khmer
    'ko':'ko.wikipedia.org',   # Korean
    'ks':'ks.wikipedia.org',   # Ekspreso, but should become Kashmiri
    'ku':'ku.wikipedia.org',   # Kurdish
    'kw':'kw.wikipedia.org',   # Cornish
    'la':'la.wikipedia.org',   # Latin
    'lb':'lb.wikipedia.org',   # Luxembourgish
    'lt':'lt.wikipedia.org',   # Latvian
    'lv':'lv.wikipedia.org',   # Livonian
    'meta':'meta.wikipedia.org', # Wikimedia meta wiki
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
    'tn':'tn.wikipedia.org',   # Tswana
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
    'zh-cn':'zh.wikipedia.org', # Simplified Chinese
    'zh-tw':'zh.wikipedia.org', # Traditional Chinese
    }

# Translation used on all Wikipedias for the different namespaces.
# (Please sort languages alphabetically)
# You only need to enter translations that differ from _default.
namespaces = {
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
        # TODO: convert all percent-encoded titles to plaintext
        '_default': u'Image',
        'af': u'Beeld',
        'ar': u'Image', # everybody seems to use the English word at the moment
        'bg': u'Картинка',
        #'bn': To be checked,
        'ca': u'Imatge',
        'cs': u'Soubor',
        'csb': u'Òbrôzk',
        'cy': u'Delwedd',
        'da': u'Billede',
        'de': u'Bild',
        'en': u'Image',
        'eo': u'Dosiero',
        'es': u'Imagen',
        'et': u'Pilt',
        'fa': u'%D8%AA%D8%B5%D9%88%DB%8C%D8%B1',
        'fi': u'Kuva',
        'fr': u'Image',
        'fy': u'Ofbyld',
        'ga': u'Íomhá',
        'he': u'%D7%AA%D7%9E%D7%95%D7%A0%D7%94',
        'hi': u'%E0%A4%9A%E0%A4%BF%E0%A4%A4%E0%A5%8D%E0%A4%B0',
        'hu': u'K%C3%A9p',
        'ia': u'Imagine',
        'id': u'Imej',
        'it': u'Immagine',
        'ja': u'%E7%94%BB%E5%83%8F',
        'ko': u'%EA%B7%B8%EB%A6%BC',
        'la': u'Imago',
        'ms': u'Imej',
        'nb': u'Bilde',
        'nl': u'Afbeelding',
        'no': u'Bilde',
        'oc': u'Image',
        'pl': u'Grafika',
        'pt': u'Imagem',
        'ro': u'Imagine',
        'ru': u'%D0%98%D0%B7%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5',
        'sk': u'Obr%C3%A1zok',
        'sl': u'Slika',
        'sq': u'Figura',
        'sr': u'%D0%A1%D0%BB%D0%B8%D0%BA%D0%B0',
        'sv': u'Bild',
        'ta': u'%E0%AE%AA%E0%AE%9F%E0%AE%BF%E0%AE%AE%E0%AE%AE%E0%AF%8D',
        'th': u'%E0%B8%A0%E0%B8%B2%E0%B8%9E',
        'wa': u'Im%C3%A5dje',
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

def namespace(code, namespace_number, fallback = '_default'):
    #print namespace_number
    #print namespaces[namespace_number]
    if namespaces[namespace_number].has_key(code):
        return namespaces[namespace_number][code]
    elif fallback:
        return namespaces[namespace_number][fallback]
    else:
        raise KeyError('ERROR: title for namespace %d in language %s unknown' % (namespace_number, code))  

# Returns the title of the special namespace in language 'code', taken from
# dictionary above.
# If the dictionary doesn't contain a translation, it will use language
# 'fallback' (English by default).
# If you want the bot to crash in case of an unknown namespace name, use
# fallback = None.
def special_namespace(code, fallback = '_default'):
    return namespace(code, -1, fallback)

def special_namespace_url(code, fallback = '_default'):
    encoded_title = namespace(code, -1, fallback).encode(code2encoding(code))
    return urllib.quote(encoded_title)

def image_namespace(code, fallback = '_default'):
    return namespace(code, 6, fallback)

def image_namespace_url(code, fallback = '_default'):
    encoded_title = namespace(code, 6, fallback).encode(code2encoding(code))
    return urllib.quote(encoded_title)

def mediawiki_namespace(code, fallback = '_default'):
    return namespace(code, 8, fallback)

def template_namespace(code, fallback = '_default'):
    return namespace(code, 10, fallback)
 
def category_namespace(code, fallback = '_default'):
    return namespace(code, 14, fallback)

def category_namespaces(code):
    namespaces = []
    namespace_title = namespace(code, 14)
    namespaces.append(namespace_title)
    namespaces.append(namespace_title.lower())
    default_namespace_title = namespace('_default', 14)
    if namespace_title != default_namespace_title:
        namespaces.append(default_namespace_title)
        namespaces.append(default_namespace_title.lower())
    return namespaces

# Redirect code can be translated, but is only in one language now.

redirect = {
    'cy': 'ail-cyfeirio',
    }

# On most Wikipedias page names must start with a capital letter, but some
# languages don't use this.

nocapitalize = ['tlh','tokipona']

# Which languages have a special order for putting interlanguage links,
# and what order is it? If a language is not in interwiki_putfirst,
# alphabetical order on language code is used. For languages that are in
# interwiki_putfirst, interwiki_putfirst is checked first, and
# languages are put in the order given there. All other languages are put
# after those, in code-alphabetical order.

alphabetic = ['af','ar','roa-rup','om','bg','be','bn','bs','br',
              'ca','chr','co','cs','cy','da','de','als','et',
              'el','en','es','eo','eu','fa','fr','fy','ga','gv',
              'gd','gl','ko','ha','hi','hr','io','id','ia','is','it',
              'he','jv','ka','csb','ks','kw','sw','la','lv','lt','hu',
              'mk','mg','ml','mi','mr','ms','zh-cfr','mn','nah','na',
              'nl','ja','no','nb','oc','nds','pl','pt','ro','ru',
              'sa','st','sq','si','simple','sk','sl','sr','su',
              'fi','sv','ta','tt','th','tlh','tw','ur','vi','tokipona',
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

#for lang in langs:
#    if not lang in special:
#        special[lang] = 'Special'
#    if not lang in image:
#        image[lang] = 'Image'

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
    return "/w/wiki.phtml?title=%s:Whatlinkshere&target=%s&limit=%d" % (special_namespace_url(code), name, config.special_page_limit)

def upload_address(code):
    return '/wiki/%s:Upload'%special_namespace_url(code)

def maintenance_address(code, maintenance_page, default_limit = True):
    if default_limit:
        return ('/w/wiki.phtml?title=%s:Maintenance&subfunction=' % special_namespace_url(code)) + maintenance_page
    else:
        return ('/w/wiki.phtml?title=%s:Maintenance&subfunction=' % special_namespace_url(code)) + maintenance_page + '&limit=' + str(config.special_page_limit)

def allmessages_address(code):
    return "/w/wiki.phtml?title=%s:Allmessages&ot=html" % special_namespace_url(code)
                        
def login_address(code):
    return '/w/wiki.phtml?title=%s:Userlogin&amp;action=submit' % special_namespace_url(code)

def move_address(code):
    return '/w/wiki.phtml?title=%s:Movepage&action=submit' % special_namespace_url(code)

def delete_address(name):
    return '/w/wiki.phtml?title=%s&action=delete' % name

def export_address(code):
    return '/wiki/%s:Export'%special_namespace_url(code)

def allpagesname(code, start):
    # This is very ugly: to get all pages, the wikipedia code
    # 'fakes' getting a page with the returned name.
    # This will need to be fixed someday.
    if version(code)=="1.2":
        return '%s:Allpages&printable=yes&from=%s'%(special_namespace_url(code), start)
    else:
        return '%s:Allpages&from=%s'%(special_namespace_url(code), start)

#
# Two functions to figure out the encoding of different languages
# This may be a lot simpler for other families!
# 

# Languages that are coded in iso-8859-1
latin1 = ['en', 'sv', 'nl', 'da', 'dk', 'test']

# Languages that used to be coded in iso-8859-1
latin1old = ['de', 'et', 'es', 'ia', 'la', 'af', 'cs', 'fr', 'pt', 'sl', 'bs', 'fy',
             'vi', 'lt', 'fi', 'it', 'no', 'simple', 'gl', 'eu',
             'nds', 'co', 'mr', 'id', 'lv', 'sw', 'tt', 'uk', 'vo',
             'ga', 'na', 'es']

            
def code2encoding(code):
    """Return the encoding for a specific language wikipedia"""
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
