#coding: iso-8859-1
"""
Library to get and put pages on Wikipedia
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2003-2004
#
# Distribute under the terms of the PSF license.
# 
__version__ = '$Id$'
#
import re, urllib, codecs, sys
import xml.sax, xml.sax.handler

import config
    
# Are we debugging this module? 0 = No, 1 = Yes, 2 = Very much so.
debug = 0
loggedin = False

# Known wikipedia languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikipedia. For human consumption,
# the full name of the language is given behind each line as a comment

langs = {
    'af':'af.wikipedia.org',   # Afrikaans
    'als':'als.wikipedia.org', # Alsatian
    'ar':'ar.wikipedia.org',   # Arabic
    'az':'az.wikipedia.org',   # Azerbaijan
    'bg':'bg.wikipedia.org',   # Bulgarian
    'bi':'bi.wikipedia.org',   # Bislama (currently also used by Bitruscan and Tok Pisin)
    'bn':'bn.wikipedia.org',   # Bengali
    'bs':'bs.wikipedia.org',   # Bosnian
    'ca':'ca.wikipedia.org',   # Catalan
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
    'ru':'ru.wikipedia.org',   # Russian
    'sa':'sa.wikipedia.org',   # Sanskrit
    'sh':'sh.wikipedia.org',   # OBSOLETE, Serbocroatian
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
    'tr':'tr.wikipedia.org',   # Turkish
    'tt':'tt.wikipedia.org',   # Tatar
    'uk':'uk.wikipedia.org',   # Ukrainian
    'ur':'ur.wikipedia.org',   # Urdu
    'vi':'vi.wikipedia.org',   # Vietnamese
    'vo':'vo.wikipedia.org',   # Volapuk
    'wa':'wikipedia.walon.org',   # Walon
    'xh':'xh.wikipedia.org',   # isiXhosa
    'yi':'yi.wikipedia.org',   # Yiddish
    'zh':'zh.wikipedia.org',   # Chinese
    'zh-cn':'zh.wikipedia.org', # Simplified Chinese
    'zh-tw':'zh.wikipedia.org', # Traditional Chinese
    }

# Languages that are coded in iso-8859-1
latin1 = ['en', 'sv', 'nl', 'de', 'es', 'da', 'dk', 'test']

# Languages that used to be coded in iso-8859-1
latin1old = ['et', 'ia', 'la', 'af', 'cs', 'fr', 'pt', 'sl', 'bs', 'fy',
             'vi', 'lt', 'fi', 'it', 'no', 'simple', 'gl', 'eu',
             'nds', 'co', 'mr', 'id', 'lv', 'sw', 'tt', 'uk', 'vo',
             'ga', 'na']

# Translation used on all wikipedia's for the Special: namespace.
# Only necessary when it is not 'Special'.
special = {
    'af': 'Spesiaal',
    'ar': '%D8%AE%D8%A7%D8%B5',
    'bg': '%D0%A1%D0%BF%D0%B5%D1%86%D0%B8%D0%B0%D0%BB%D0%BD%D0%B8',
    'bn': '%E0%A6%AC%E0%A6%BF%E0%A6%B6%E0%A7%87%E0%A6%B7',
    'ca': 'Especial',
    'cs': 'Speci%C3%A1ln%C3%AD',
    'csb': 'Specjalna',
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
    'csb': 'Imagem',
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

redirect = {
    'cy': 'ail-cyfeirio',
    }

# Defaults for Special: and Image: namespace names

for lang in langs:
    if not lang in special:
        special[lang] = 'Special'
    if not lang in image:
        image[lang] = 'Image'

obsolete = ['sh', 'dk', 'wa']

# A few selected big languages for things that we do not want to loop over
# all languages.
biglangs = ['da', 'de', 'en', 'es', 'fr', 'ja', 'nl', 'pl', 'sv']

biglangs2 = biglangs + [
            'ca', 'eo', 'et', 'fi', 'he', 'it', 'no', 'pt', 'ro', 'sl',
            'zh']

biglangs3 = biglangs2 + [
            'af', 'cs', 'eu', 'gl', 'hr', 'ia', 'id', 'la', 'ms', 'ru',
            'simple']

seriouslangs  = biglangs3 + [
                'ar', 'bg', 'bs', 'cy', 'el', 'fa', 'fy', 'hi', 'hu', 'ko',
                'is', 'ku', 'lt', 'lv', 'nds', 'oc', 'sr', 'ta', 'th', 'tr',
                'uk', 'vi']

# other groups of language that we might want to do at once

cyrilliclangs = ['bg', 'mk', 'ru', 'sr', 'uk'] # languages in Cyrillic

# Set needput to True if you want write-access to the Wikipedia.
needput = True 

# This is used during the run-time of the program to store all character
# sets encountered for each of the wikipedia languages.
charsets = {}

# Keep the modification time of all downloaded pages for an eventual put.
edittime = {}

# Which languages have a special order for putting interlanguage links,
# and what order is it? If a language is not in interwiki_putfirst,
# alphabetical order on language code is used. For languages that are in
# interwiki_putfirst, interwiki_putfirst is checked first, and
# languages are put in the order given there. All other languages are put
# after those, in code-alphabetical order.

interwiki_putfirst = {
    'en':['af','ar','om','bg','bn','bs','ca','co','cs','cy','da',
          'de','als','et','el','en','es','eo','eu','fa','fr',
          'fy','ga','gv','gd','gl','ko','hi','hr','id','is',
          'it','ia','he','jv','ka','csb','ks','sw','la','lv',
          'lt','hu','mk','mg','ml','mi','mr','ms','nah','na',
          'nl','ja','no','nb','oc','nds','pl','pt','ro','ru','sa',
          'st','sq','simple','sk','sl','sr','su','fi','sv','ta',
          'tt','th','ur','vi','tr','uk','vo','yi','zh','zh-cn',
          'zh-tw'],
    'fr':['af','ar','om','bg','bn','bs','ca','co','cs','cy','da',
          'de','als','et','el','en','es','eo','eu','fa','fr',
          'fy','ga','gv','gd','gl','ko','hi','hr','id','is',
          'it','ia','he','jv','ka','csb','ks','sw','la','lv',
          'lt','hu','mk','mg','ml','mi','mr','ms','nah','na',
          'nl','ja','no','nb','oc','nds','pl','pt','ro','ru','sa',
          'st','sq','simple','sk','sl','sr','su','fi','sv','ta',
          'tt','th','ur','vi','tr','uk','vo','yi','zh','zh-cn',
          'zh-tw'],
    'hu':['en'],
    'pl':['af','ar','om','bg','bn','bs','ca','co','cs','cy','da',
          'de','als','et','el','en','es','eo','eu','fa','fr',
          'fy','ga','gv','gd','gl','ko','hi','hr','id','is',
          'it','ia','he','jv','ka','csb','ks','sw','la','lv',
          'lt','hu','mk','mg','ml','mi','mr','ms','nah','na',
          'nl','ja','no','nb','oc','nds','pl','pt','ro','ru','sa',
          'st','sq','simple','sk','sl','sr','su','fi','sv','ta',
          'tt','th','ur','vi','tr','uk','vo','yi','zh','zh-cn',
          'zh-tw'],
    }

# Local exceptions

class Error(Exception):
    """Wikipedia error"""

class NoPage(Error):
    """Wikipedia page does not exist"""

class IsRedirectPage(Error):
    """Wikipedia page is a redirect page"""

class IsNotRedirectPage(Error):
    """Wikipedia page is not a redirect page"""

class LockedPage(Error):
    """Wikipedia page is locked"""

class NoSuchEntity(ValueError):
    """No entity exist for this character"""

class SubpageError(ValueError):
    """The subpage specified by # does not exist"""

SaxError = xml.sax._exceptions.SAXParseException

# The most important thing in this whole module: The PageLink class
class PageLink:
    """A Wikipedia page link."""
    def __init__(self, code, name = None, urlname = None,
                 linkname = None, incode = None):
        """Constructor. Normally called with two arguments:
             1) The language code on which the page resides
             2) The name of the page as suitable for a URL

             The argument incode can be specified to help decode
             the name; it is the language where this link was found.
        """     
        self._incode = incode
        self._code = code
        if linkname is None and urlname is None and name is not None:
            # Clean up the name, it can come from anywhere.
            name = name.strip()
            if name and name[0]==':':
                name=name[1:]
            self._urlname = link2url(name, self._code, incode = self._incode)
            self._linkname = url2link(self._urlname, code = self._code,
                                      incode = mylang)
        elif linkname is not None:
            # We do not trust a linkname either....
            name = linkname.strip()
            if name and name[0]==':':
                name=name[1:]
            self._urlname = link2url(name, self._code, incode=self._incode)
            self._linkname = url2link(self._urlname, code = self._code,
                                      incode = mylang)
        elif urlname is not None:
            self._urlname = urlname
            self._linkname = url2link(urlname, code = self._code,
                                      incode = mylang)

    def urlname(self):
        """The name of the page this PageLink refers to, in a form suitable
           for the URL of the page."""
        return self._urlname

    def linkname(self):
        """The name of the page this PageLink refers to, in a form suitable
           for a wiki-link"""
        return self._linkname

    def hashname(self):
        """The name of the subpage this PageLink refers to. Subpages are
           denominated by a # in the linkname(). If no subpage is referenced,
           None is returned."""
        ln = self.linkname()
        ln = re.sub('&#', '&hash;', ln)
        if not '#' in ln:
            return None
        else:
            hn = ln[ln.find('#') + 1:]
            hn = re.sub('&hash;', '&#', hn)
            #print "hn=", hn
            return hn

    def hashfreeLinkname(self):
        hn=self.hashname()
        if hn:
            return self.linkname()[:-len(hn)-1]
        else:
            return self.linkname()
            
    def code(self):
        """The code for the language of the page this PageLink refers to,
           without :"""
        return self._code

    def ascii_linkname(self):
        return url2link(self._urlname, code = self._code, incode = 'ascii')
        
    def __str__(self):
        """A simple ASCII representation of the pagelink"""
        return "%s:%s" % (self._code, self.ascii_linkname())

    def __repr__(self):
        """A more complete string representation"""
        return "PageLink{%s}" % str(self)

    def aslink(self):
        """A string representation in the form of an interwiki link"""
        return "[[%s:%s]]" % (self.code(), self.linkname())

    def asselflink(self):
        """A string representation in the form of a local link, but prefixed by
           the language code"""
        return "%s:[[%s]]" % (self.code(), self.linkname())

    def asasciilink(self):
        """A string representation in the form of an interwiki link"""
        return "[[%s:%s]]" % (self.code(), self.ascii_linkname())

    def asasciiselflink(self):
        """A string representation in the form of a local link, but prefixed by
           the language code"""
        return "%s:[[%s]]" % (self.code(), self.ascii_linkname())
    
    def get(self):
        """The wiki-text of the page. This will retrieve the page if it has not
           been retrieved yet. This can raise the following exceptions that
           should be caught by the calling code:

            NoPage: The page does not exist

            IsRedirectPage: The page is a redirect. The argument of the
                            exception is the page it redirects to.

            LockedPage: The page is locked, and therefore its contents can
                        not be retrieved.

            SubpageError: The subject does not exist on a page with a # link
        """
        # Make sure we re-raise an exception we got on an earlier attempt
        if hasattr(self, '_redirarg'):
            raise IsRedirectPage,self._redirarg
        if hasattr(self, '_getexception'):
            raise self._getexception
        # Make sure we did try to get the contents once
        if not hasattr(self, '_contents'):
            try:
                self._contents = getPage(self.code(), self.urlname())
                hn = self.hashname()
                if hn:
                    hn = underline2space(hn)
                    m = re.search("== *%s *==" % hn, self._contents)
                    if not m:
                        raise SubpageError("Hashname does not exist: %s" % self)
            except NoPage:
                self._getexception = NoPage
                raise
            except IsRedirectPage,arg:
                self._getexception = IsRedirectPage
                self._redirarg = arg
                raise
            except LockedPage:
                self._getexception = LockedPage
                raise
            except SubpageError:
                self._getexception = SubpageError
                raise
        return self._contents

    def exists(self):
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        except SubpageError:
            return False
        return True

    def isRedirectPage(self):
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        return False
    
    def isEmpty(self):
        txt = self.get()
        if len(removeLanguageLinks(txt)) < 4:
            return 1
        else:
            return 0
        
    def put(self, newtext, comment=None, watchArticle = '0', minorEdit = '1'):
        """Replace the new page with the contents of the first argument.
           The second argument is a string that is to be used as the
           summary for the modification
        """
        return putPage(self.code(), self.urlname(), newtext, comment, watchArticle, minorEdit)

    def interwiki(self):
        """Return a list of inter-wiki links in the page. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of PageLink objects for each of the
           interwiki links in the page text.
        """
        result = []
        ll = getLanguageLinks(self.get(), incode = self.code())
        for newcode,newname in ll.iteritems():
            if newname[0] == ':':
                print "ERROR> link from %s to %s:%s has leading :?!"%(self,newcode,repr(newname))
            if newname[0] == ' ':
                print "ERROR> link from %s to %s:%s has leading space?!"%(self,newcode,repr(newname))
            try:
                result.append(self.__class__(newcode, linkname=newname,
                                             incode = self.code()))
            except UnicodeEncodeError:
                print "ERROR> link from %s to %s:%s is invalid encoding?!"%(self,newcode,repr(newname))
            except NoSuchEntity:
                print "ERROR> link from %s to %s:%s contains invalid character?!"%(self,newcode,repr(newname))
            except ValueError:
                print "ERROR> link from %s to %s:%s contains invalid unicode reference?!"%(self,newcode,repr(newname))
        return result

    def __cmp__(self, other):
        """Pseudo method to be able to use equality and inequality tests on
           PageLink objects"""
        #print "__cmp__", self, other
        if not hasattr(other, 'code'):
            return -1
        if not self.code() == other.code():
            return cmp(self.code(), other.code())
        u1=html2unicode(self.linkname(), language = self.code())
        u2=html2unicode(other.linkname(), language = other.code())
        return cmp(u1,u2)

    def __hash__(self):
        """Pseudo method that makes it possible to store PageLink objects as
           keys in hash-tables.
        """
        return hash(str(self))

    def links(self):
        # Gives the normal (not-interwiki) pages the page redirects to, as PageLinks
        result = []
        try:
            thistxt = removeLanguageLinks(self.get())
        except IsRedirectPage:
            pass
        w=r'([^\]\|]*)'
        Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
        for l in Rlink.findall(thistxt):
            result.append(l[0])
        return result

    def imagelinks(self):
        result = []
        im=image[self._code] + ':'
        w1=r'('+im+'[^\]\|]*)'
        w2=r'([^\]]*)'
        Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
        for l in Rlink.findall(self.get()):
            result.append(PageLink(self._code,l[0]))
        w1=r'('+im.lower()+'[^\]\|]*)'
        w2=r'([^\]]*)'
        Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
        for l in Rlink.findall(self.get()):
            result.append(PageLink(self._code,l[0]))
        return result

    def getRedirectTo(self):
        # Given a redirect page, gives the page it redirects to
        try:
            self.get()
        except IsRedirectPage, arg:
            return arg
        else:
            raise IsNotRedirectPage(self)
        

# Regular expression recognizing redirect pages

def redirectRe(code):
    if redirect.has_key(code):
        txt = '(?:redirect|'+redirect[code]+')'
    else:
        txt = 'redirect'
    return re.compile(r'\#'+txt+':? *\[\[(.*?)\]\]', re.I)

# Shortcut get to get multiple pages at once
class WikimediaXmlHandler(xml.sax.handler.ContentHandler):
    def setCallback(self, callback):
        self.callback = callback
        
    def startElement(self, name, attrs):
        self.destination = None
        if name == 'page':
            self.text=u''
            self.title=u''
            self.timestamp=u''
        elif name == 'text':
            self.destination = 'text'
        elif name == 'title':
            self.destination = 'title'
        elif name == 'timestamp':
            self.destination = 'timestamp'

    def endElement(self, name):
        if name == 'revision':
            # All done for this.
            # print "DBG> ",repr(self.title), self.timestamp, len(self.text)
            # Uncode the text
            text = unescape(self.text)
            # Remove trailing newlines and spaces
            while text and text[-1] in '\n ':
                text = text[:-1]
            # Replace newline by cr/nl
            text = u'\r\n'.join(text.split('\n'))
            # Decode the timestamp
            timestamp = (self.timestamp[0:4]+
                         self.timestamp[5:7]+
                         self.timestamp[8:10]+
                         self.timestamp[11:13]+
                         self.timestamp[14:16]+
                         self.timestamp[17:19])
            # Report back to the caller
            self.callback(self.title.strip(), timestamp, text)
            
    def characters(self, data):
        if self.destination == 'text':
            self.text += data
        elif self.destination == 'title':
            self.title += data
        elif self.destination == 'timestamp':
            self.timestamp += data
            
class GetAll:
    debug = 0
    addr = '/wiki/%s:Export'
    def __init__(self, code, pages):
        self.code = code
        self.pages = []
        for pl in pages:
            if not hasattr(pl,'_contents') and not hasattr(pl,'_getexception'):
                self.pages.append(pl)
            else:
                print "BUGWARNING: %s already done!"%pl.asasciilink()

    def run(self):
        data = self.getData()
        handler = WikimediaXmlHandler()
        handler.setCallback(self.oneDone)
        try:
            xml.sax.parseString(data, handler)
        except xml.sax._exceptions.SAXParseException:
            f=open('sax_parse_bug.dat','w')
            f.write(data)
            f.close()
            print "Dumped invalid XML to sax_parse_bug.dat"
            raise
        # All of the ones that have not been found apparently do not exist
        for pl in self.pages:
            if not hasattr(pl,'_contents') and not hasattr(pl,'_getexception'):
                pl._getexception = NoPage

    def oneDone(self, title, timestamp, text):
        #print "DBG>", repr(title), timestamp, len(text)
        pl = PageLink(self.code, title)
        for pl2 in self.pages:
            #print "DBG>", pl, pl2, pl2.hashfreeLinkname()
            if PageLink(self.code, pl2.hashfreeLinkname()) == pl:
                if not hasattr(pl2,'_contents') and not hasattr(pl2,'_getexception'):
                    break
        else:
            print repr(title)
            print repr(pl)
            print repr(self.pages)
            print "BUG> bug, page not found in list"
        if self.debug:
            xtext = pl2.get()
            if text != xtext:
                print "################Text differs"
                import difflib
                for line in difflib.ndiff(xtext.split('\r\n'), text.split('\r\n')):
                    if line[0] in ['+', '-']:
                        print repr(line)[2:-1]
            if edittime[self.code, link2url(title, self.code)] != timestamp:
                print "################Timestamp differs"
                print "-",edittime[self.code, link2url(title, self.code)]
                print "+",timestamp
        else:
            m = redirectRe(self.code).match(text)
            if m:
                #print "DBG> ",pl2.asasciilink(),"is a redirect page"
                pl2._getexception = IsRedirectPage(m.group(1))
            else:
                if len(text)<50:
                    print "DBG> short text in",pl2.asasciilink()
                    print repr(text)
                hn = pl2.hashname()
                if hn:
                    m = re.search("== *%s *==" % hn, text)
                    if not m:
                        pl2._getexception = SubpageError("Hashname does not exist: %s" % self)
                    else:
                        # Store the content
                        pl2._contents = text
                        # Store the time stamp
                        edittime[self.code, link2url(title, self.code)] = timestamp
                else:
                    # Store the content
                    pl2._contents = text
                    # Store the time stamp
                    edittime[self.code, link2url(title, self.code)] = timestamp

    def getData(self):
        import httplib
        addr = self.addr%special[self.code]
        pagenames = u'\r\n'.join([x.hashfreeLinkname() for x in self.pages])
        pagenames = forCode(pagenames, self.code)
        data = urlencode((
                    ('action', 'submit'),
                    ('pages', pagenames),
                    ('curonly', 'True'),
                    ))
        #print repr(data)
        headers = {"Content-type": "application/x-www-form-urlencoded", 
                   "User-agent": "RobHooftWikiRobot/1.0"}
        # Slow ourselves down
        get_throttle(requestsize = len(self.pages))
        # Now make the actual request to the server
        conn = httplib.HTTPConnection(langs[self.code])
        conn.request("POST", addr, data, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
    
def getall(code, pages):
    #print "DBG> getall", code, pages
    print "Getting %d pages from %s:"%(len(pages),code) 
    return GetAll(code, pages).run()
    
# Library functions

def PageLinksFromFile(fn):
    f=open(fn, 'r')
    R=re.compile(r'\[\[([^:]*):([^\]]*)\]\]')
    for line in f.readlines():
        m=R.match(line)
        if m:
            yield PageLink(m.group(1), m.group(2))
        else:
            print "ERROR: Did not understand %s line:\n%s" % (fn, repr(line))
    f.close()
    
def unescape(s):
    """Replace escaped HTML-special characters by their originals"""
    if '&' not in s:
        return s
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&") # Must be last
    return s

def setAction(s):
    """Set a summary to use for changed page submissions"""
    global action
    action = s

# Default action
setAction('Wikipedia python library')

def urlencode(query):
    """This can encode a query so that it can be sent as a query using
       a http POST request"""
    l=[]
    for k, v in query:
        k = urllib.quote(k)
        v = urllib.quote(v)
        l.append(k + '=' + v)
    return '&'.join(l)


Rmorespaces = re.compile('  +')

def space2underline(name):
    name = Rmorespaces.sub(' ', name)
    return name.replace(' ', '_')

Rmoreunderlines = re.compile('__+')

def underline2space(name):
    name = Rmoreunderlines.sub('_', name)
    return name.replace('_', ' ')

# Mechanics to slow down page download rate.

import time

class Throttle:
    def __init__(self, delay = config.throttle, ignore = 0):
        """Make sure there are at least 'delay' seconds between page-gets
           after 'ignore' initial page-gets"""
        self.delay = delay
        self.ignore = ignore
        self.now = 0
        self.next_multiplicity = 1.0

    def setDelay(self, delay = config.throttle):
        self.delay = delay

    def waittime(self):
        """Calculate the time in seconds we will have to wait if a query
           would be made right now"""
        if self.ignore > 0:
            return 0.0
        # Take the previous requestsize in account calculating the desired
        # delay this time
        thisdelay = self.next_multiplicity * self.delay
        now = time.time()
        ago = now - self.now
        if ago < thisdelay:
            delta = thisdelay - ago
            return delta
        else:
            return 0.0
        
    def __call__(self, requestsize = 1):
        """This is called from getPage without arguments. It will make sure
           that if there are no 'ignores' left, there are at least delay seconds
           since the last time it was called before it returns."""
        if self.ignore > 0:
            self.ignore -= 1
        else:
            waittime = self.waittime()
            # Calculate the multiplicity of the next delay based on how
            # big the request is that is being posted now.
            # We want to add "one delay" for each factor of two in the
            # size of the request. Getting 64 pages at once allows 6 times
            # the delay time for the server.
            import math
            self.next_multiplicity = math.log(1+requestsize)/math.log(2.0)
            # Announce the delay if it exceeds a preset limit
            if waittime > config.noisysleep:
                print "Sleeping for %.1f seconds" % waittime
            time.sleep(waittime)
        self.now = time.time()

get_throttle = Throttle()
put_throttle = Throttle(config.put_throttle)

def putPage(code, name, text, comment = None, watchArticle = '0', minorEdit = '1'):
    """Upload 'text' on page 'name' to the 'code' language wikipedia.
       Use of this routine can normally be avoided; use PageLink.put
       instead.
    """
    import httplib
    put_throttle()
    host = langs[code]
    address = '/w/wiki.phtml?title=%s&action=submit'%space2underline(name)
    if comment is None:
        comment=action
    if not loggedin or code != mylang:
        comment = username + ' - ' + comment
    try:
        text = forCode(text, code)
        data = urlencode((
            ('wpMinoredit', minorEdit),
            ('wpSave', '1'),
            ('wpWatchthis', watchArticle),
            ('wpEdittime', edittime[code, link2url(name, code)]),
            ('wpSummary', comment),
            ('wpTextbox1', text)))
    except KeyError:
        print edittime
	raise
    if debug:
        print text
        print address
        print data
        return None, None, None
    conn = httplib.HTTPConnection(host)

    conn.putrequest("POST", address)

    conn.putheader('Content-Length', str(len(data)))
    conn.putheader("Content-type", "application/x-www-form-urlencoded")
    conn.putheader("User-agent", "RobHooftWikiRobot/1.0")
    if cookies and code == mylang:
        conn.putheader('Cookie',cookies)
    conn.endheaders()
    conn.send(data)

    response = conn.getresponse()
    data = response.read()
    conn.close()
    return response.status, response.reason, data

def forCode(text, code):
    """Prepare the unicode string 'text' for inclusion into a page for
       language 'code'. All of the characters in the text should be encodable,
       otherwise this will fail! This condition is normally met, except if
       you would copy text verbatim from an UTF-8 language into a iso-8859-1
       language, and none of the robots in the package should do such things"""
    if type(text) == type(u''):
        if code == 'ascii':
            return UnicodeToAsciiHtml(text)
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(code2encoding(code))
        text,l = encode_func(text)
    return text

class MyURLopener(urllib.FancyURLopener):
    version="RobHooftWikiRobot/1.0"
    
def getUrl(host,address):
    """Low-level routine to get a URL from wikipedia"""
    #print host,address
    uo = MyURLopener()
    if cookies:
        uo.addheader('Cookie', cookies)
    f = uo.open('http://%s%s'%(host, address))
    text = f.read()
    #print f.info()
    ct = f.info()['Content-Type']
    R = re.compile('charset=([^\'\"]+)')
    m = R.search(ct)
    if m:
        charset = m.group(1)
    else:
        charset = None
    #print text
    return text,charset
    
def getPage(code, name, do_edit = 1, do_quote = 1):
    """Get the contents of page 'name' from the 'code' language wikipedia
       Do not use this directly; use the PageLink object instead."""
    print "Getting page %s:%s"%(code,name)
    host = langs[code]
    name = re.sub(' ', '_', name)
    if not '%' in name and do_quote: # It should not have been done yet
        if name != urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    address = '/w/wiki.phtml?title='+name+"&redirect=no"
    if do_edit:
        address += '&action=edit&printable=yes'
    if debug:
        print host, address
    # Make sure Brion doesn't get angry by slowing ourselves down.
    get_throttle()
    text, charset = getUrl(host,address)
    # Extract the actual text from the textedit field
    if do_edit:
        if debug:
            print "Raw:", len(text), type(text), text.count('x')
        if charset is None:
            print "WARNING: No character set found"
        else:
            # Store character set for later reference
            if charsets.has_key(code):
                assert charsets[code].lower() == charset.lower(), "charset for %s changed from %s to %s"%(code,charsets[code],charset)
            charsets[code] = charset
            if code2encoding(code).lower() != charset.lower():
                raise ValueError("code2encodings has wrong charset for %s. It should be %s"%(code,charset))
            
        if debug>1:
            print repr(text)
        m = re.search('value="(\d+)" name=\'wpEdittime\'',text)
        if m:
            edittime[code, link2url(name, code)] = m.group(1)
        else:
            m = re.search('value="(\d+)" name="wpEdittime"',text)
            if m:
                edittime[code, link2url(name, code)] = m.group(1)
            else:
                edittime[code, link2url(name, code)] = 0
        try:
            i1 = re.search('<textarea[^>]*>', text).end()
        except AttributeError:
            print "BUG: Yikes: No text area.",host,address
            print repr(text)
            raise NoPage(code, name)
        i2 = re.search('</textarea>', text).start()
        if i2-i1 < 2:
            raise NoPage(code, name)
        if debug:
            print text[i1:i2]
        m = redirectRe(code).match(text[i1:i2])
        if m:
            print "DBG> %s is redirect to %s"%(name,m.group(1))
            raise IsRedirectPage(m.group(1))
        if edittime[code, name] == 0:
            print "DBG> page may be locked?!"
            pass
            #raise LockedPage()

        x = text[i1:i2]
        x = unescape(x)
        while x and x[-1] in '\n ':
            x = x[:-1]
    else:
        x = text # If not editing
        
    # Convert to a unicode string
    encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(charset)
    try:
        x,l = decode_func(x)
    except UnicodeError:
        print code,name
        print repr(x)
        raise 
    return x

def languages(first = []):
    """Return a list of language codes for known wikipedia servers. If a list
       of language codes is given as argument, these will be put at the front
       of the returned list."""
    result = []
    for key in first:
        if key in langs.iterkeys():
            result.append(key)
    for key in seriouslangs:
        if key not in result:
            result.append(key)
    return result

def allpages(start = '%21%200'):
    """Iterate over all Wikipedia pages in the home language, starting
       at the given page."""
    start = link2url(start, code = mylang)
    m=0
    while 1:
        text = getPage(mylang, '%s:Allpages&printable=yes&from=%s'%(special[mylang],start),do_quote=0,do_edit=0)
        #print text
        R = re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        n = 0
        for hit in R.findall(text):
            if not ':' in hit:
                # Some dutch exceptions.
                if not hit in ['Hoofdpagina','In_het_nieuws']:
                    n = n + 1
                    yield PageLink(mylang, url2link(hit, code = mylang,
                                                    incode = mylang))
                    start = hit + '%20%200'
        if n < 100:
            break
        m += n
        sys.stderr.write('AllPages: %d done; continuing from "%s";\n'%(m,url2link(start,code='nl',incode='ascii')))


# Part of library dealing with interwiki links

def getLanguageLinks(text,incode=None):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}. Do not call this routine directly, use
       PageLink objects instead"""
    result = {}
    for code in langs:
        m=re.search(r'\[\['+code+':([^\]]*)\]\]', text)
        if m:
            if m.group(1):
                t=m.group(1)
                if '|' in t:
                    t=t[:t.index('|')]
                if incode == 'eo':
                    t=t.replace('xx','x')
                if code in obsolete:
                    print "ERROR: ignoring link to obsolete language %s:%s"%(
                        code, repr(t))
                else:
                    result[code] = t
            else:
                print "ERROR: empty link to %s:"%(code)
    if incode in ['zh','zh-cn','zh-tw']:
        m=re.search(u'\\[\\[([^\\]\\|]*)\\|\u7b80\\]\\]', text)
        if m:
            #print "DBG> found link to traditional Chinese", repr(m.group(0))
            result['zh-cn'] = m.group(1)
        m=re.search(u'\\[\\[([^\\]\\|]*)\\|\u7c21\\]\\]', text)
        if m:
            #print "DBG> found link to traditional Chinese", repr(m.group(0))
            result['zh-cn'] = m.group(1)
        m=re.search(u'\\[\\[([^\\]\\|]*)\\|\u7e41\\]\\]', text)
        if m:
            #print "DBG> found link to simplified Chinese", repr(m.group(0))
            result['zh-tw'] = m.group(1)
    return result

def removeLanguageLinks(text):
    """Given the wiki-text of a page, return that page with all interwiki
       links removed. If a link to an unknown language is encountered,
       a warning is printed."""
    for code in langs:
        text = re.sub(r'\[\['+code+':([^\]]*)\]\]', '', text)
    m=re.search(r'\[\[([a-z][a-z]):([^\]]*)\]\]', text)
    if m:
        print "WARNING: Link to unknown language %s name %s"%(m.group(1), repr(m.group(2)))
    # Remove white space at the beginning
    while 1:
        if text and text.startswith('\r\n'):
            text=text[2:]
        elif text and text.startswith(' '):
            # This assumes that the first line NEVER starts with a space!
            text=text[1:]
        else:
            break
    # Remove white space at the end
    while 1:
        if text and text[-1:] in '\r\n \t':
            text=text[:-1]
        else:
            break
    # Add final newline back in
    text += '\n'
    return text

def replaceLanguageLinks(oldtext, new):
    """Replace the interwiki language links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a dictionary with the language names as keys, and
       either PageLink objects or the link-names of the pages as values.
    """   
    s = interwikiFormat(new)
    s2 = removeLanguageLinks(oldtext)
    if s:
        if mylang in config.interwiki_attop:
            newtext = s + config.interwiki_text_separator + s2
        else:
            newtext = s2 + config.interwiki_text_separator + s
    else:
        newtext = s2
    return newtext
    
def interwikiFormat(links):
    """Create a suitable string encoding all interwiki links for a wikipedia
       page.

       'links' should be a dictionary with the language names as keys, and
       either PageLink objects or the link-names of the pages as values.

       The string is formatted for inclusion in mylang.
    """
    if not links:
        return ''
    s = []
    ar = links.keys()
    ar.sort()
    if mylang in interwiki_putfirst:
        #In this case I might have to change the order
        ar2 = []
        for code in interwiki_putfirst[mylang]:
            if code in ar:
                del ar[ar.index(code)]
                ar2 = ar2 + [code]
        ar = ar2 + ar
    for code in ar:
        try:
            s.append(links[code].aslink())
        except AttributeError:
            s.append('[[%s:%s]]' % (code, links[code]))
    if mylang in config.interwiki_on_one_line:
        sep = ' '
    else:
        sep = '\r\n'
    s=sep.join(s) + '\r\n'
    return s 
            
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

def url2link(percentname,incode,code):
    """Convert a url-name of a page into a proper name for an interwiki link
       the argument 'incode' specifies the encoding of the target wikipedia
       """
    result = underline2space(percentname)
    x = url2unicode(result, language = code)
    e = code2encoding(incode)
    if e == 'utf-8':
        # utf-8 can handle anything
        return x
    elif e == code2encoding(code):
        #print "url2link", repr(x), "same encoding",incode,code
        return unicode2html(x, encoding = code2encoding(code))
    else:
        # In all other cases, replace difficult chars by &#; refs.
        #print "url2link", repr(x), "different encoding"
        return unicode2html(x, encoding = 'ascii')
    
def link2url(name, code, incode = None):
    """Convert a interwiki link name of a page to the proper name to be used
       in a URL for that page. code should specify the language for the link"""
    if code == 'eo':
        name = name.replace('cx','&#265;')
        name = name.replace('Cx','&#264;')
        name = name.replace('CX','&#264;')
        name = name.replace('gx','&#285;')
        name = name.replace('Gx','&#284;')
        name = name.replace('GX','&#284;')
        name = name.replace('hx','&#293;')
        name = name.replace('Hx','&#292;')
        name = name.replace('HX','&#292;')
        name = name.replace('jx','&#309;')
        name = name.replace('Jx','&#308;')
        name = name.replace('JX','&#308;')
        name = name.replace('sx','&#349;')
        name = name.replace('Sx','&#348;')
        name = name.replace('SX','&#348;')
        name = name.replace('ux','&#365;')
        name = name.replace('Ux','&#364;')
        name = name.replace('UX','&#364;')
        name = name.replace('&#265;x','cx')
        name = name.replace('&#264;x','Cx')
        name = name.replace('&#264;X','CX')
        name = name.replace('&#285;x','gx')
        name = name.replace('&#284;x','Gx')
        name = name.replace('&#284;X','GX')
        name = name.replace('&#293;x','hx')
        name = name.replace('&#292;x','Hx')
        name = name.replace('&#292;X','HX')
        name = name.replace('&#309;x','jx')
        name = name.replace('&#308;x','Jx')
        name = name.replace('&#308;X','JX')
        name = name.replace('&#349;x','sx')
        name = name.replace('&#348;x','Sx')
        name = name.replace('&#348;X','SX')
        name = name.replace('&#365;x','ux')
        name = name.replace('&#364;x','Ux')
        name = name.replace('&#364;X','UX')
    if '%' in name:
        try:
            name = url2unicode(name, language = code)
        except UnicodeEncodeError:
            name = html2unicode(name, language = code, altlanguage = incode)
    else:
        name = html2unicode(name, language = code, altlanguage = incode)

    #print "DBG>",repr(name)
    # Remove spaces from beginning and the end
    name = name.strip()
    # Standardize capitalization
    if name:
        name = name[0].upper()+name[1:]
    #print "DBG>",repr(name)
    try:
        result = str(name.encode(code2encoding(code)))
    except UnicodeError:
        print "Cannot convert %s into a URL for %s" % (repr(name), code)
        # Put entities in there. The URL will not be found.
        result = addEntity(name)
        #raise
    result = space2underline(result)
    return urllib.quote(result)


def getReferences(pl):
    host = langs[pl.code()]
    url = "/w/wiki.phtml?title=%s:Whatlinkshere&target=%s"%(special[mylang], pl.urlname())
    txt, charset = getUrl(host,url)
    Rref = re.compile('<li><a href.*="([^"]*)"')
    x = Rref.findall(txt)
    x.sort()
    # Remove duplicates
    for i in range(len(x)-1, 0, -1):
        if x[i] == x[i-1]:
            del x[i]
    return x

######## Unicode library functions ########

def UnicodeToAsciiHtml(s):
    html = []
    for c in s:
        cord = ord(c)
        #print cord,
        if cord < 128:
            html.append(c)
        else:
            html.append('&#%d;'%cord)
    #print
    return ''.join(html)

def url2unicode(percentname, language):
    x=urllib.unquote(str(percentname))
    #print "DBG> ",language,repr(percentname),repr(x)
    # Try utf-8 first. It almost cannot succeed by accident!
    for encoding in ('utf-8',)+code2encodings(language):
        try:
            encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
            x,l = decode_func(x)
            #print "DBG> ",encoding,repr(x)
            return x
        except UnicodeError:
            pass
    raise UnicodeError("Could not decode %s" % repr(percentname))

def unicode2html(x, encoding='latin1'):
    # We have a unicode string. We can attempt to encode it into the desired
    # format, and if that doesn't work, we encode the unicode into html #
    # entities. If it does work, we return it unchanged.
    try:
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
        y,l = encode_func(x)
    except UnicodeError:
        x = UnicodeToAsciiHtml(x)
    return x
    
def removeEntity(name):
    import htmlentitydefs
    Rentity = re.compile(r'&([A-Za-z]+);')
    result = u''
    i = 0
    while i < len(name):
        m = Rentity.match(name[i:])
        if m:
            if htmlentitydefs.name2codepoint.has_key(m.group(1)):
                x = htmlentitydefs.name2codepoint[m.group(1)]
                result = result + unichr(x)
                i += m.end()
            else:
                result += name[i]
                i += 1
        else:
            result += name[i]
            i += 1
    return result

def addEntity(name):
    """Convert a unicode name into ascii name with entities"""
    import htmlentitydefs
    result = ''
    for c in name:
        if ord(c) < 128:
            result += str(c)
        else:
            for k, v in htmlentitydefs.entitydefs.iteritems():
                if (len(v) == 1 and ord(c) == ord(v)) or v == '&#%d;'%ord(c):
                    result += '&%s;' % k
                    break
            else:
                result += '&#%d;' % ord(c)
    #print "DBG> addEntity:", repr(name), repr(result)
    return result

def unicodeName(name, language, altlanguage = None):
    for encoding in code2encodings(language):
        try:
            if type(name)==type(u''):
                return name
            else:
                return unicode(name, encoding)
        except UnicodeError:
            continue
    if altlanguage is not None:
        print "DBG> Using local encoding!", altlanguage, "to", language, name
        for encoding in code2encodings(altlanguage):
            try:
                return unicode(name, encoding)
            except UnicodeError:
                continue
    raise Error("Cannot decode")
    #return unicode(name,code2encoding(inlanguage))
    
def html2unicode(name, language, altlanguage=None):
    name = unicodeName(name, language, altlanguage)
    name = removeEntity(name)

    Runi = re.compile('&#(\d+);')
    Runi2 = re.compile('&#x([0-9a-fA-F]+);')
    result = u''
    i=0
    while i < len(name):
        m = Runi.match(name[i:])
        m2 = Runi2.match(name[i:])
        if m:
            result += unichr(int(m.group(1)))
            i += m.end()
        elif m2:
            result += unichr(int(m2.group(1),16))
            i += m2.end()
        else:
            try:
                result += name[i]
                i += 1
            except UnicodeDecodeError:
                print repr(name)
                raise
    return result

def setMyLang(code):
    """Change the home language"""
    global mylang
    global cookies

    mylang = code
    # Retrieve session cookies for login.
    try:
        f = open('%s-login.data' % mylang)
        cookies = '; '.join([x.strip() for x in f.readlines()])
        loggedin = True
        #print cookies
        f.close()
    except IOError:
        #print "Not logged in"
        cookies = None
        loggedin = False

def checkLogin():
    global loggedin
    txt = getPage(mylang,'Non-existing page', do_edit = 0)
    loggedin = 'Userlogin' not in txt
    return loggedin
    
def argHandler(arg):
    if arg.startswith('-lang:'):
        setMyLang(arg[6:])
    elif arg.startswith('-throttle:'):
        get_throttle.setDelay(int(arg[10:]))
    elif arg.startswith('-putthrottle:'):
        put_throttle.setDelay(int(arg[13:]))
    elif arg == '-nil':
        return 1
    else:
        return 0
    return 1

#########################
# Interpret configuration 
#########################

# Get the name of the user for submit messages
username = config.username
if not config.username:
    print "Please make a file user-config.py, and put in there:"
    print "One line saying \"username='yy'\""
    print "One line saying \"mylang='xx'\""
    print "....filling in your real name and home wikipedia."
    print "for other possible configuration variables check config.py"
    sys.exit(1)
setMyLang(config.mylang)
if not langs.has_key(mylang):
    print "Home-wikipedia from user-config.py does not exist"
    print "Defaulting to test: wikipedia"
    setMyLang('test')
    langs['test']='test.wikipedia.org'
