# -*- coding: utf-8  -*-

import config, urllib

# Parent class for all wiki families

class Family:
    langs = {}

    namespaces = {}

    for i in range(-2,16):
        namespaces[i]={}

def namespace(code, namespace_number, fallback = '_default'):
    if namespaces[namespace_number].has_key(code):
        return namespaces[namespace_number][code]
    elif fallback:
        return namespaces[namespace_number][fallback]
    else:
        raise KeyError('ERROR: title for namespace %d in language %s unknown' % (namespace_number, code))  

# Returns the title of the special namespace in language 'code', taken from
# dictionary above.
# If the dictionary doesn't contain a translation, it will use language
# 'fallback' (or, if fallback isn't given, MediaWiki default).
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

    redirect = {}

    # On most Wikipedias page names must start with a capital letter, but some
    # languages don't use this.

    nocapitalize = []

    # Which languages have a special order for putting interlanguage links,
    # and what order is it? If a language is not in interwiki_putfirst,
    # alphabetical order on language code is used. For languages that are in
    # interwiki_putfirst, interwiki_putfirst is checked first, and
    # languages are put in the order given there. All other languages are put
    # after those, in code-alphabetical order.

    interwiki_putfirst = {}

    # Which languages do no longer exist and should trigger a warning?
    obsolete = []

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    biglangs = []

    biglangs2 = biglangs + []

    biglangs3 = biglangs2 + []

    biglangs4 = biglangs3 + []

    seriouslangs = biglangs4 + []

    # other groups of language that we might want to do at once

    # languages in Cyrillic
    cyrilliclangs = []

    # Methods
    
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

    def code2encoding(code):
        """Return the encoding for a specific language wikipedia"""
        return 'utf-8'

    def code2encodings(code):
        """Return a list of historical encodings for a specific language
           wikipedia"""
        return code2encoding(code),
    
