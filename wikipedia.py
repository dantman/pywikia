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
import re,urllib,codecs,sys

# Are we debugging this module? 0 = No, 1 = Yes, 2 = Very much so.
debug = 0

# Known wikipedia languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikipedia. For human consumption,
# the full name of the language is given behind each line as a comment

langs = {'en':'en.wikipedia.org', # English
         'pl':'pl.wikipedia.org', # Polish, UTF-8
         'da':'da.wikipedia.org', # Danish
         'sv':'sv.wikipedia.org', # Swedish
         'zh':'zh.wikipedia.org', # Chinese, UTF-8
         'eo':'eo.wikipedia.org', # Esperanto, UTF-8
         'nl':'nl.wikipedia.org', # Dutch
         'de':'de.wikipedia.org', # German
         'fr':'fr.wikipedia.org', # French
         'es':'es.wikipedia.org', # Spanish
         'cs':'cs.wikipedia.org', # Czech, UTF-8
         'ru':'ru.wikipedia.org', # Russian, UTF-8
         'ja':'ja.wikipedia.org', # Japanese, UTF-8
         'sl':'sl.wikipedia.org', # Slovenian, UTF-8
         'ko':'ko.wikipedia.org', # Korean, UTF-8
         'hu':'hu.wikipedia.org', # Hungarian, UTF-8
         'el':'el.wikipedia.org', # Grieks, UTF-8
         'bs':'bs.wikipedia.org', # Bosnisch, UTF-8
	 'he':'he.wikipedia.org', # Hebrew, UTF-8
         'hi':'hi.wikipedia.org', # Hindi, UTF-8
         'nds':'nds.wikipedia.org', # Lower Saxon
         'ro':'ro.wikipedia.org', # Romanian, UTF-8
         'fy':'fy.wikipedia.org', # Frisian, UTF-8
         'ar':'ar.wikipedia.org', # Arabic, UTF-8
         'zh-tw':'zh.wikipedia.org', # Traditional Chinese, UTF-8
         'zh-cn':'zh.wikipedia.org', # Simplified Chinese, UTF-8
         'it':'it.wikipedia.org', # Italian
         'no':'no.wikipedia.org', # Norwegian
         'pt':'pt.wikipedia.org', # Portuguese
         'af':'af.wikipedia.org', # Afrikaans
         'la':'la.wikipedia.org', # Latin
         'ca':'ca.wikipedia.org', # Catalan
         'fi':'fi.wikipedia.org', # Finnish
         'ia':'ia.wikipedia.org', # Interlingua
         'et':'et.wikipedia.org', # Estonian
         'eu':'eu.wikipedia.org', # Basque
         'hr':'hr.wikipedia.org', # Croatian, UTF-8
         'tr':'tr.wikipedia.org', # Turkish, UTF-8
         'mr':'mr.wikipedia.org', # ?
         'cy':'cy.wikipedia.org', # Welsh, UTF-8
         'simple':'simple.wikipedia.org', # Simplified english
         #'test':'test.wikipedia.org',
         }

# Languages that are coded in iso-8859-1
latin1 = ['en', 'da', 'sv', 'nl', 'de', 'es', 'fr', 'nds', 'it',
          'no', 'pt', 'af', 'la', 'ca', 'fi', 'ia', 'et', 'eu',
          'mr', 'simple' ]

# Languages that used to be coded in iso-8859-1
latin1old = ['cs', 'sl', 'bs', 'fy']

# Translation used on all wikipedia's for the Special: namespace.
# This is e.g. used by the login script.
special = {'en':'Special',
           'nl':'Speciaal',
           'da':'Speciel',
           'de':'Spezial',
           'fr':'Special',
           'fy':'Wiki',
           'eo':'Speciala',
           'es':'Especial',
           'ia':'Special',
           'it':'Speciale',
           'pl':'Specjalna',
           'ro':'Special',
           'sv':'Special'
           }

# Wikipedia's out of the list that are not running the phase-III software,
# given as a list of language codes.
oldsoftware = ['it', 'no', 'pt', 'af', 'la', 'ca', 'fi', 'ia', 'et', 'eu',
               'simple', 'nds', 'mr']

# A few selected big languages for things that we do not want to loop over
# all languages.
biglangs = ['en', 'pl', 'da', 'sv', 'nl', 'de', 'fr', 'es']

# Set needput to True if you want write-access to the Wikipedia.
needput = True 

# This is used during the run-time of the program to store all character
# sets encountered for each of the wikipedia languages.
charsets = {}

# Keep the modification time of all downloaded pages for an eventual put.
edittime = {}

# Local exceptions

class Error(Exception):
    """Wikipedia error"""

class NoPage(Error):
    """Wikipedia page does not exist"""

class IsRedirectPage(Error):
    """Wikipedia page does not exist"""

class LockedPage(Error):
    """Wikipedia page is locked"""

class NoSuchEntity(ValueError):
    """No entity exist for this character"""

class SubpageError(ValueError):
    """The subpage specified by # does not exist"""
    
# The most important thing in this whole module: The PageLink class
class PageLink:
    """A Wikipedia page link."""
    def __init__(self, code, name = None, urlname = None,
                 linkname = None, incode = None):
        """Constructor. Normally called with two arguments:
             1) The language code on which the page resides
             2) The name of the page as suitable for a URL
        """     
        self._incode = incode
        self._code = code
        if linkname is None and urlname is None and name is not None:
            # Clean up the name, it can come from anywhere.
            name = name.strip()
            self._urlname = link2url(name, self._code, incode = self._incode)
            self._linkname = url2link(self._urlname, code = self._code,
                                      incode = self._incode)
        elif linkname is not None:
            # We do not trust a linkname either....
            name = linkname.strip()
            self._urlname = link2url(name, self._code, incode=self._incode)
            self._linkname = url2link(self._urlname, code = self._code,
                                      incode = self._incode)
        elif urlname is not None:
            self._urlname = urlname
            self._linkname = url2link(urlname, code = self._code,
                                      incode = self._incode)

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
        
    def code(self):
        """The code for the language of the page this PageLink refers to,
           without :"""
        return self._code
    
    def __str__(self):
        """A simple ASCII representation of the pagelink"""
        nm = url2link(self._urlname, code = self._code, incode = 'ascii')
        return "%s:%s" % (self._code, nm)

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
    
    def get(self):
        """The wiki-text of the page. This will retrieve the page if it has not
           been retrieved yet. This can raise the following exceptions that
           should be caught by the calling code:

            NoPage: The page does not exist

            IsRedirectPage: The page is a redirect. The argument of the
                            exception is the page it redirects to.

            LockedPage: The page is locked, and therefore its contents can
                        not be retrieved.
        """
        if not hasattr(self, '_contents'):
            self._contents = getPage(self.code(), self.urlname())
            hn = self.hashname()
            if hn:
                m = re.search("== *%s *==" % hn, self._contents)
                if not m:
                    raise SubpageError("Hashname does not exist: %s" % self)
                
        return self._contents

    def put(self,newtext,comment=None):
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
        #print "__cmp__",repr(u1),repr(u2)
        return cmp(u1,u2)

    def __hash__(self):
        """Pseudo method that makes it possible to store PageLink objects as
           keys in hash-tables.
        """
        return hash(str(self))
    
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
    l=[]
    for k, v in query:
        k = urllib.quote(str(k))
        v = urllib.quote(str(v))
        l.append(k + '=' + v)
    return '&'.join(l)

def space2underline(name):
    return name.replace(' ', '_')

def underline2space(name):
    return name.replace('_', ' ')

# Mechanics to slow down page download rate.

import time

class Throttle:
    def __init__(self, delay = 6, ignore = 0):
        """Make sure there are at least 'delay' seconds between page-gets
           after 'ignore' initial page-gets"""
        self.delay = delay
        self.ignore = ignore
        self.now = 0

    def __call__(self,newdelay=None):
        """This is called from getPage without arguments. It will make sure
           that if there are no 'ignores' left, there are at least delay seconds
           since the last time it was called before it returns.

           A new delay can be set by calling this function with an argument
           giving the desired delay in seconds."""
        if newdelay is not None:
            self.delay = newdelay
        elif self.ignore > 0:
            self.ignore -= 1
        else:
            now = time.time()
            ago = now - self.now
            if ago < self.delay:
                time.sleep(self.delay - ago)
            self.now = time.time()

throttle=Throttle()

def putPage(code, name, text, comment = None):
    """Upload 'text' on page 'name' to the 'code' language wikipedia."""
    import httplib
    host = langs[code]
    if code in oldsoftware:
        raise Error("Cannot put pages on old wikipedia software")
    address = '/w/wiki.phtml?title=%s&action=submit'%space2underline(name)
    if comment is None:
        comment=action
    if not loggedin or code != mylang:
        comment = username + ' - ' + comment
    try:
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
    if cookies and code == mylang:
        conn.putheader('Cookie',cookies)
    conn.endheaders()
    conn.send(data)

    response = conn.getresponse()
    data = response.read()
    conn.close()
    return response.status, response.reason, data

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
            address += '&action=edit'
    else:
        if not do_edit:
            raise "can not skip edit on old-software wikipedia"
        address = '/wiki.cgi?action=edit&id='+name
    if debug:
        print host, address
    # Make sure Brion doesn't get angry by slowing ourselves down.
    throttle()
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
            raise NoPage()
        if debug:
            print text[i1:i2]
        if text[i1:i2] == 'Describe the new page here.\n': # old software
            raise NoPage()
        Rredirect = re.compile(r'\#redirect:? *\[\[(.*?)\]\]', re.I)
        m=Rredirect.match(text[i1:i2])
        if m:
            raise IsRedirectPage(m.group(1))
        if needput:
            assert edittime[code, name] != 0 or code in oldsoftware, "No edittime on non-empty page?! %s:%s\n%s"%(code,name,text)

        x = text[i1:i2]
        x = unescape(x)
    else:
        x = text # If not editing
        
    if charset == 'utf-8':
        # Make it to a unicode string
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('utf-8')
        try:
            x,l = decode_func(x)
        except UnicodeError:
            print code,name
            print repr(x)
            raise 
        # Convert the unicode characters to &# references, and make it ascii.
        x = str(UnicodeToAsciiHtml(x))
    return x

def languages(first = []):
    """Return a list of language codes for known wikipedia servers. If a list
       of language codes is given as argument, these will be put at the front
       of the returned list."""
    result = []
    for key in first:
        if key in langs.iterkeys():
            result.append(key)
    for key in langs.iterkeys():
        if key not in result:
            result.append(key)
    return result

def allpages(start = '%21%200'):
    """Iterate over all Wikipedia pages in the home language, starting
       at the given page. This will raise an exception if the home language
       does not have a translation of 'Special' listed above."""
    import sys
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
    return result

def removeLanguageLinks(text):
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
            text=text[1:]
        else:
            break
    return text
    
def interwikiFormat(links):
    """Create a suitable string to start a wikipedia page consisting of
       interwikilinks given as a dictionary of code:pagename in the argument.
    """
    s = []
    ar = links.keys()
    ar.sort()
    for code in ar:
        try:
            s.append(links[code].aslink())
        except AttributeError:
            s.append('[[%s:%s]]' % (code, links[code]))
    return ' '.join(s) + '\r\n'
            
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
        return 'utf-8','iso-8859-2'
    if code == 'ru':
        return 'utf-8','iso-8859-5'
    if code in latin1old:
        return 'utf-8','iso-8859-1'
    return code2encoding(code),
    
def url2link(percentname,incode,code):
    """Convert a url-name of a page into a proper name for an interwiki link
       the argument 'incode' specifies the encoding of the target wikipedia
       """
    result = underline2space(percentname)
    x = url2unicode(result, language = code)
    if code2encoding(incode) == code2encoding(code):
        #print "url2link", repr(x), "same encoding"
        return unicode2html(x, encoding = code2encoding(code))
    else:
        #print "url2link", repr(x), "different encoding"
        return unicode2html(x, encoding = 'ascii')
    
def link2url(name, code, incode = None):
    """Convert a interwiki link name of a page to the proper name to be used
       in a URL for that page. code should specify the language for the link"""
    if '%' in name:
        name = url2unicode(name, language = code)
    else:
        name = html2unicode(name, language = code, altlanguage = incode)
    # Remove spaces from beginning and the end
    name = name.strip()
    # Standardize capitalization
    if name:
        name = name[0].upper()+name[1:]
    try:
        result = str(name.encode(code2encoding(code)))
    except UnicodeError:
        print "Cannot convert %s into a URL for %s" % (repr(name), code)
        # Put entities in there.
        result = addEntity(name)
        #raise
    result = space2underline(result)
    return urllib.quote(result)

######## Unicode library functions ########

def UnicodeToAsciiHtml(s):
    html = []
    i=0
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
    x=urllib.unquote(percentname)
    for encoding in code2encodings(language):
        try:
            encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
            x,l = decode_func(x)
            return x
        except UnicodeError:
            pass
    raise UnicodeError("Could not decode %s" % repr(percentname))

def unicode2html(x, encoding='latin1'):
    # We have a unicode string. We can attempt to encode it into the desired
    # format, and if that doesn't work, we encode the unicode into html #
    # entities.
    try:
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
        x,l = encode_func(x)
        #print "unicode2html",x
    except UnicodeError:
        x = UnicodeToAsciiHtml(x)
    return str(x)
    
def removeEntity(name):
    import re, htmlentitydefs
    Rentity = re.compile(r'&([A-Za-z]+);')
    result = ''
    i = 0
    while i < len(name):
        m = Rentity.match(name[i:])
        if m:
            if htmlentitydefs.entitydefs.has_key(m.group(1)):
                result = result + htmlentitydefs.entitydefs[m.group(1)]
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
    print "DBG> addEntity:", repr(name), repr(result)
    return result

def unicodeName(name, language, altlanguage = None):
    for encoding in code2encodings(language):
        try:
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
    raise "Cannot decode"
    #return unicode(name,code2encoding(inlanguage))
    
def html2unicode(name, language, altlanguage=None):
    name = removeEntity(name)
    name = unicodeName(name, language, altlanguage)

    import re
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

#########################
# Read configuration files: username.dat and login.data
#########################

# Get the name of the user for submit messages
try:
    f = open('username.dat')
    username = f.readline()[:-1]
    try:
        mylang = f.readline()[:-1]
    except IOError:
        print "No Home-wikipedia given in username.dat"
        print "Defaulting to test: wikipedia"
        mylang = 'test'
        langs['test']='test.wikipedia.org'
    if not langs.has_key(mylang):
        print "Home-wikipedia from username.dat does not exist"
        print "Defaulting to test: wikipedia"
        mylang = 'test'
        langs['test']='test.wikipedia.org'
    f.close()
except IOError:
    print >> sys.stderr, "Please make a file username.dat with your name in there"
    sys.exit(1)

# Retrieve session cookies for login.
try:
    f = open('login.data')
    cookies = '; '.join([x.strip() for x in f.readlines()])
    #print cookies
    f.close()
except IOError:
    cookies = None
