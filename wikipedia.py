#coding: iso-8859-1
"""
Library to get and put pages on Wikipedia
"""
#
# (C) Rob W.W. Hooft, 2003
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
    'ar':'ar.wikipedia.org',   # Arabic, UTF-8
    'bs':'bs.wikipedia.org',   # Bosnian, UTF-8
    'ca':'ca.wikipedia.org',   # Catalan
    'cs':'cs.wikipedia.org',   # Czech, UTF-8
    'cy':'cy.wikipedia.org',   # Welsh, UTF-8
    'da':'da.wikipedia.org',   # Danish
    'de':'de.wikipedia.org',   # German
    'el':'el.wikipedia.org',   # Greek, UTF-8
    'en':'en.wikipedia.org',   # English
    'eo':'eo.wikipedia.org',   # Esperanto, UTF-8
    'es':'es.wikipedia.org',   # Spanish
    'et':'et.wikipedia.org',   # Estonian
    'eu':'eu.wikipedia.org',   # Basque
    'fi':'fi.wikipedia.org',   # Finnish, UTF-8
    'fr':'fr.wikipedia.org',   # French
    'fy':'fy.wikipedia.org',   # Frisian, UTF-8
    'ga':'ga.wikipedia.org',   # Irish Gaelic
    'gl':'gl.wikipedia.org',   # Galician
    'he':'he.wikipedia.org',   # Hebrew, UTF-8
    'hi':'hi.wikipedia.org',   # Hindi, UTF-8
    'hr':'hr.wikipedia.org',   # Croatian, UTF-8
    'hu':'hu.wikipedia.org',   # Hungarian, UTF-8
    'ia':'ia.wikipedia.org',   # Interlingua
    'id':'id.wikipedia.org',   # Indonesian
    'it':'it.wikipedia.org',   # Italian, UTF-8
    'ja':'ja.wikipedia.org',   # Japanese, UTF-8
    'ko':'ko.wikipedia.org',   # Korean, UTF-8
    'la':'la.wikipedia.org',   # Latin
    'lt':'lt.wikipedia.org',   # Latvian
    'lv':'lv.wikipedia.org',   # Livonian
    'ml':'ml.wikipedia.org',   # Malayalam (UTF-8?)
    'mr':'mr.wikipedia.org',   # Marathi
    'ms':'ms.wikipedia.org',   # Malaysian
    'nah':'nah.wikipedia.org', # Nahuatl (UTF-8?)
    'nds':'nds.wikipedia.org', # Lower Saxon
    'nl':'nl.wikipedia.org',   # Dutch
    'no':'no.wikipedia.org',   # Norwegian
    'oc':'oc.wikipedia.org',   # Occitan, UTF-8
    'pl':'pl.wikipedia.org',   # Polish, UTF-8
    'pt':'pt.wikipedia.org',   # Portuguese
    'ro':'ro.wikipedia.org',   # Romanian, UTF-8
    'ru':'ru.wikipedia.org',   # Russian, UTF-8
    'simple':'simple.wikipedia.org', # Simple English
    'sl':'sl.wikipedia.org',   # Slovenian, UTF-8
    'sq':'sq.wikipedia.org',   # Albanian (UTF-8?)
    'sr':'sr.wikipedia.org',   # Serbian, UTF-8
    'sv':'sv.wikipedia.org',   # Swedish
    'sw':'sw.wikipedia.org',   # Swahili
    'test':'test.wikipedia.org',
    'tr':'tr.wikipedia.org',   # Turkish, UTF-8
    'tt':'tt.wikipedia.org',   # Tatar
    'uk':'uk.wikipedia.org',   # Ukrainian (Latin-1?)
    'vi':'vi.wikipedia.org',   # Vietnamese
    'vo':'vo.wikipedia.org',   # Volapuk
    'zh':'zh.wikipedia.org',   # Chinese, UTF-8
    'zh-cn':'zh.wikipedia.org', # Simplified Chinese, UTF-8
    'zh-tw':'zh.wikipedia.org', # Traditional Chinese, UTF-8
    }

# Languages that are coded in iso-8859-1
latin1 = ['en', 'sv', 'nl', 'de', 'es', 'fr', 'nds',
          'no', 'pt', 'af', 'la', 'ca', 'ia', 'et', 'eu',
          'mr', 'id', 'simple', 'gl', 'lv', 'sw',
          'tt', 'uk', 'vo', 'ga', 'da', 'test']

# Languages that used to be coded in iso-8859-1
latin1old = ['cs', 'sl', 'bs', 'fy', 'vi', 'lt', 'fi', 'it']

# Translation used on all wikipedia's for the Special: namespace.
# This is e.g. used by the login script.
special = {
    'ar': 'Special',
    'bs': 'Special',
    'cs': 'Speci%C3%A1ln%C3%AD',
    'da': 'Speciel',
    'de': 'Spezial',
    'en': 'Special',
    'eo': 'Speciala',
    'es': 'Especial',
    'fi': 'Toiminnot',
    'fr': 'Special',
    'fy': 'Wiki',
    'he': '%D7%9E%D7%99%D7%95%D7%97%D7%93',
    'hr': 'Special',
    'hu': 'Speci%C3%A1lis',
    'el': 'Special',
    'ia': 'Special',
    'it': 'Speciale',
    'ja': '%E7%89%B9%E5%88%A5',
    'ko': '%ED%8A%B9%EC%88%98%EA%B8%B0%EB%8A%A5',
    'ms': 'Special',
    'nl': 'Speciaal',
    'pl': 'Specjalna',
    'ro': 'Special',
    'ru': 'Special',
    'sl': 'Posebno',
    'sr': '%D0%9F%D0%BE%D1%81%D0%B5%D0%B1%D0%BD%D0%BE',
    'sq': 'Special',
    'sv': 'Special',
    'test': 'Special',
    'zh': 'Special',
    'zh-cn': 'Special',
    'zh-tw': 'Special',
    }

# Wikipedia's out of the list that are not running the phase-III software,
# given as a list of language codes.
oldsoftware = ['no', 'pt', 'af', 'la', 'ca', 'ia', 'et', 'eu',
               'simple', 'nds', 'mr', 'id', 'gl', 'lv', 'sw',
               'tt', 'uk', 'vo', 'ga']

# A few selected big languages for things that we do not want to loop over
# all languages.
biglangs = ['en', 'pl', 'da', 'sv', 'nl', 'de', 'fr', 'es']

# And a larger selection in case we say 'all languages' but don't really
# mean 'all'
seriouslangs = ['af', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo',
                'es', 'et', 'fi', 'fr', 'fy', 'gl', 'he', 'hr', 'hu',
                'ia', 'it', 'ja', 'ko', 'la', 'ms', 'nds', 'nl', 'no',
                'oc', 'pl', 'pt', 'ro', 'ru', 'sl', 'sr', 'sv', 'zh',
                'simple']

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
    'en':['af','ar','ms','bs','ca','cs','cy','da','de',
          'et','el','en','es','eo','eu','fr','fy','ga',
          'gl','ko','hi','hr','id','it','ia','he','sw',
          'la','lv','lt','hu','ml','mr','nah','nl','ja',
          'no','oc','nds','pl','pt','ro','ru','sq','simple',
          'sl','sr','fi','sv','tt','vi','tr','uk','vo',
          'zh','zh-cn','zh-tw'],
    'fr':['af','ar','ms','bs','ca','cs','cy','da','de',
          'et','el','en','es','eo','eu','fr','fy','ga',
          'gl','ko','hi','hr','id','it','ia','he','sw',
          'la','lv','lt','hu','ml','mr','nah','nl','ja',
          'no','oc','nds','pl','pt','ro','ru','sq','simple',
          'sl','sr','fi','sv','tt','vi','tr','uk','vo',
          'zh','zh-cn','zh-tw'],
    'hu':['en'],
    'pl':['af','sq','en','ar','eu','bs','zh','zh-tw','zh-cn',
          'hr','cs','da','eo','et','fi','fr','fy','gl',
          'el','he','hi','es','nl','id','ia','ga','ja',
          'ca','ko','la','lv','ml','ms','mr','de','no',
          'pt','oc','ru','ro','sl','sr','sw','sv','tt',
          'tr','uk','simple','vo','cy','hu','vi','it'],
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

# Regular expression recognizing redirect pages

Rredirect = re.compile(r'\#redirect:? *\[\[(.*?)\]\]', re.I)

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
            self._urlname = link2url(name, self._code, incode = self._incode)
            self._linkname = url2link(self._urlname, code = self._code,
                                      incode = mylang)
        elif linkname is not None:
            # We do not trust a linkname either....
            name = linkname.strip()
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
                self._getexception = IsRedirectPage,arg
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
        return True

    def isRedirectPage(self):
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        return False
    
    def put(self, newtext, comment=None):
        """Replace the new page with the contents of the first argument.
           The second argument is a string that is to be used as the
           summary for the modification
        """
        return putPage(self.code(), self.urlname(), newtext, comment)

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
    
    def getRedirectTo(self):
        # Given a redirect page, gives the page it redirects to
        try:
            self.get()
        except IsRedirectPage, arg:
            return arg
        else:
            raise IsNotRedirectPage(self)

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
            while text[-1] in '\n ':
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
            print data
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
            print title
            print pl
            print self.pages
            raise "bug, page not found in list"
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
            m=Rredirect.match(text)
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
        data = urlencode((
                    ('action', 'submit'),
                    ('pages', pagenames),
                    ('curonly', 'True'),
                    ))
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
    if code in oldsoftware:
        return
    #print "DBG> getall", code, pages
    print "Getting %d pages from %s:"%(len(pages),code) 
    return GetAll(code, pages).run()
    
# Library functions
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

def space2underline(name):
    return name.replace(' ', '_')

def underline2space(name):
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
        
    def __call__(self, requestsize = 1):
        """This is called from getPage without arguments. It will make sure
           that if there are no 'ignores' left, there are at least delay seconds
           since the last time it was called before it returns.

           A new delay can be set by calling this function with an argument
           giving the desired delay in seconds."""
        if self.ignore > 0:
            self.ignore -= 1
        else:
            # Take the previous requestsize in account calculating the desired
            # delay this time
            thisdelay = self.next_multiplicity * self.delay
            # Calculate the multiplicity of the next delay based on how
            # big the request is that is being posted now.
            # We want to add "one delay" for each factor of two in the
            # size of the request. Getting 64 pages at once allows 6 times
            # the delay time for the server.
            import math
            self.next_multiplicity = math.log(1+requestsize)/math.log(2.0)
            # Calculate how long it has been since the last request
            now = time.time()
            ago = now - self.now
            # Wait if we need to.
            if ago < thisdelay:
                delta = thisdelay - ago
                if delta > config.noisysleep:
                    print "Sleeping for %.1f seconds" % delta
                time.sleep(delta)
            self.now = time.time()

get_throttle = Throttle()
put_throttle = Throttle(config.put_throttle)

def putPage(code, name, text, comment = None):
    """Upload 'text' on page 'name' to the 'code' language wikipedia.
       Use of this routine can normally be avoided; use PageLink.put
       instead.
    """
    import httplib
    put_throttle()
    host = langs[code]
    if code in oldsoftware:
        raise Error("Cannot put pages on old wikipedia software")
    address = '/w/wiki.phtml?title=%s&action=submit'%space2underline(name)
    if comment is None:
        comment=action
    if not loggedin or code != mylang:
        comment = username + ' - ' + comment
    try:
        text = forCode(text, code)
        data = urlencode((
            ('wpSummary', comment),
            ('wpMinoredit', '1'),
            ('wpSave', '1'),
            ('wpEdittime', edittime[code, link2url(name, code)]),
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
    if code in oldsoftware:
        # Old algorithm
        name = re.sub('_', ' ', name)
        n = []
        for x in name.split():
            n.append(x[0].capitalize() + x[1:])
        name = '_'.join(n)
        #print name
    else:
        name = re.sub(' ', '_', name)
    if not '%' in name and do_quote: # It should not have been done yet
        if name != urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    if code not in oldsoftware:
        address = '/w/wiki.phtml?title='+name+"&redirect=no"
        if do_edit:
            address += '&action=edit&printable=yes'
    else:
        if not do_edit:
            raise Error("can not skip edit on old-software wikipedia")
        address = '/wiki.cgi?action=edit&id='+name
    if debug:
        print host, address
    # Make sure Brion doesn't get angry by slowing ourselves down.
    get_throttle()
    text, charset = getUrl(host,address)
    # Keep login status for external use
    if code == mylang:
        global loggedin
        if "Userlogin" in text:
            loggedin = False
        else:
            loggedin = True
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
            #print "No text area.",host,address
            #print repr(text)
            raise LockedPage(text)
        i2 = re.search('</textarea>', text).start()
        if i2-i1 < 2: # new software
            raise NoPage(code, name)
        if debug:
            print text[i1:i2]
        if text[i1:i2] == 'Describe the new page here.\n': # old software
            raise NoPage(code, name)
        m=Rredirect.match(text[i1:i2])
        if m:
            print "DBG> %s is redirect to %s"%(name,m.group(1))
            raise IsRedirectPage(m.group(1))
        if edittime[code, name] == 0 and code not in oldsoftware:
            print "DBG> page may be locked?!"
            pass
            #raise LockedPage()

        x = text[i1:i2]
        x = unescape(x)
        while x[-1] in '\n ':
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
       at the given page. This will raise an exception if the home language
       does not have a translation of 'Special' listed above."""
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
                result[code] = t
            else:
                print "ERROR: empty link to %s:"%(code)
    if incode in ['zh','zh-cn','zh-tw']:
        m=re.search(u'\\[\\[([^\\]\\|]*)\\|\u7b80\\]\\]', text)
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
        text=re.sub(r'\[\['+code+':([^\]]*)\]\]', '', text)
    m=re.search(r'\[\[([a-z][a-z]):([^\]]*)\]\]', text)
    if m:
        print "WARNING: Link to unknown language %s name %s"%(m.group(1), m.group(2))
    # Remove white space at the beginning
    while 1:
        if text.startswith('\r\n'):
            text=text[2:]
        elif text.startswith(' '):
            # This assumes that the first line NEVER starts with a space!
            text=text[1:]
        else:
            break
    # Remove white space at the end
    while 1:
        if text[-1:] in '\r\n \t':
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
        if mylang in config.interwiki_atbottom:
            newtext = s2 + config.interwiki_text_separator + s
        else:
            newtext = s + config.interwiki_text_separator + s2
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
    if mylang in config.interwiki_on_separate_lines:
        sep = '\r\n'
    else:
        sep = ' '
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
    if code2encoding(incode) == 'utf-8':
        # utf-8 can handle anything
        return x
    elif code2encoding(incode) == code2encoding(code):
        #print "url2link", repr(x), "same encoding",incode,code
        return unicode2html(x, encoding = code2encoding(code))
    else:
        # In all other cases, replace difficult chars by &#; refs.
        #print "url2link", repr(x), "different encoding"
        return unicode2html(x, encoding = 'ascii')
    
def link2url(name, code, incode = None):
    """Convert a interwiki link name of a page to the proper name to be used
       in a URL for that page. code should specify the language for the link"""
    if '%' in name:
        name = url2unicode(name, language = code)
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
        # Put entities in there.
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
    for encoding in code2encodings(language):
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
                raise NoSuchEntity("Cannot locate entity for character %s"%repr(c))
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
    result = u''
    i=0
    while i < len(name):
        m = Runi.match(name[i:])
        if m:
            result += unichr(int(m.group(1)))
            i += m.end()
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
        #print cookies
        f.close()
    except IOError:
        #print "Not logged in"
        cookies = None

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
