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

#
# Import the user's family. If not changed in user_config, the family
# is Wikipedia.
#

exec("import %s_family as family"%config.family)

# Set needput to True if you want write-access to the Wikipedia.
needput = True 

# This is used during the run-time of the program to store all character
# sets encountered for each of the wikipedia languages.
charsets = {}

# Keep the modification time of all downloaded pages for an eventual put.
edittime = {}

# Languages to use for comment text after the actual language but before
# en:. For example, if for language 'xx', you want the preference of
# languages to be:
# xx:, then fr:, then ru:, then en:
# you let altlang return ['fr','ru'].
# This code is used by chooselang below.

def altlang(code):
    if code in ['fa','ku']:
        return ['ar']
    if code=='sk':
        return ['cs']
    if code=='nds':
        return ['de','nl']
    if code in ['ca','gn','nah']:
        return ['es']
    if code=='eu':
        return ['es','fr']
    if code=='gl':
        return ['es','pt']
    if code in ['oc','th','vi','wa']:
        return ['fr']
    if code=='als':
        return ['fr','de']
    if code=='co':
        return ['fr','it']
    if code=='fy':
        return ['nl']
    if code=='csb':
        return ['pl']
    if code in ['mo','roa-rup']:
        return ['ro']
    if code in ['be','lt','lv','uk']:
        return ['ru']
    if code in ['ja','ko','za','zh','zh-cfr','zh-cn','zh-tw']:
        return ['zh','zh-cn','zh-tw']
    if code=='da':
        return ['nb','no']
    if code in ['is','no','nb']:
        return ['no','nb','nn','da']
    if code=='sv':
        return ['da','no','nb']
    if code in ['id','jv','ms','su']:
        return ['id','ms','jv','su']
    if code in ['bs','hr','mk','sh','sr']:
        return ['hr','sr','bs']
    if code=='ia':
        return ['la','es','fr','it']
    if code=='sa':
        return ['hi']
    if code=='yi':
        return ['he']
    if code=='bi':
        return ['tpi']
    if code=='tpi':
        return ['bi']
    return []

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

    def aslocallink(self):
        """A string representation in the form of a local link"""
        return "[[%s]]" % (self.linkname())

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
        if self.exists():
            newPage="0"
        else:
            newPage="1"
        return putPage(self.code(), self.urlname(), newtext, comment, watchArticle, minorEdit, newPage)

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

    def categories(self):
        result = []
        ll = getCategoryLinks(self.get(),self.code())
        for catname in ll:
            result.append(self.__class__(self.code(), linkname=catname))
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
        # Gives the normal (not-interwiki, non-category) pages the page
        # directs to, as strings
        result = []
        try:
            thistxt = removeLanguageLinks(self.get())
        except IsRedirectPage:
            pass
        try:
            thistxt = removeCategoryLinks(self.get(), self.code())
        except IsRedirectPage:
            pass
        w=r'([^\]\|]*)'
        Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
        for l in Rlink.findall(thistxt):
            result.append(l[0])
        return result

    def imagelinks(self):
        result = []
        im=family.image[self._code] + ':'
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
    if family.redirect.has_key(code):
        txt = '(?:redirect|'+family.redirect[code]+')'
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
            text = self.text
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
            elif hasattr(pl,'_contents') and pl.code()=="eo":
                # Edit-pages use X-convention, XML export does not. Double
                # X-es where necessary.
                pl._contents = pl._contents.replace('CX','CXX')
                pl._contents = pl._contents.replace('Cx','Cxx')
                pl._contents = pl._contents.replace('cx','cxx')
                pl._contents = pl._contents.replace('GX','GXX')
                pl._contents = pl._contents.replace('Gx','Gxx')
                pl._contents = pl._contents.replace('gx','gxx')
                pl._contents = pl._contents.replace('HX','HXX')
                pl._contents = pl._contents.replace('Hx','Hxx')
                pl._contents = pl._contents.replace('hx','hxx')
                pl._contents = pl._contents.replace('JX','JXX')
                pl._contents = pl._contents.replace('Jx','Jxx')
                pl._contents = pl._contents.replace('jx','jxx')
                pl._contents = pl._contents.replace('SX','SXX')
                pl._contents = pl._contents.replace('Sx','Sxx')
                pl._contents = pl._contents.replace('sx','sxx')
                pl._contents = pl._contents.replace('UX','UXX')
                pl._contents = pl._contents.replace('Ux','Uxx')
                pl._contents = pl._contents.replace('ux','uxx')
                # Also would have liked to do this part, but I must have done
                # something wrong.
                # pl._contents = pl._contents.replace('%C4%89','cx')
                # pl._contents = pl._contents.replace('%C4%88','CX')
                # pl._contents = pl._contents.replace('%C4%9D','gx')
                # pl._contents = pl._contents.replace('%C4%9C','GX')
                # pl._contents = pl._contents.replace('%C4%A5','hx')
                # pl._contents = pl._contents.replace('%C4%A4','HX')
                # pl._contents = pl._contents.replace('%C4%B5','jx')
                # pl._contents = pl._contents.replace('%C4%B4','JX')
                # pl._contents = pl._contents.replace('%C5%9D','sx')
                # pl._contents = pl._contents.replace('%C5%9C','SX')
                # pl._contents = pl._contents.replace('%C5%AD','ux')
                # pl._contents = pl._contents.replace('%C5%AC','UX')

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
        addr = family.export_address(self.code)
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
        conn = httplib.HTTPConnection(family.hostname(self.code))
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

def putPage(code, name, text, comment = None, watchArticle = '0', minorEdit = '1', newPage = '0'):
    """Upload 'text' on page 'name' to the 'code' language wikipedia.
       Use of this routine can normally be avoided; use PageLink.put
       instead.
    """
    import httplib
    put_throttle()
    host = family.hostname(code)
    address = family.put_address(code, space2underline(name))
    if comment is None:
        comment=action
    if not loggedin or code != mylang:
        comment = username + ' - ' + comment
    try:
        text = forCode(text, code)
        if newPage=='1':
            data = urlencode((
                ('wpMinoredit', minorEdit),
                ('wpSave', '1'),
                ('wpWatchthis', watchArticle),
                ('wpEdittime', ''),
                ('wpSummary', comment),
                ('wpTextbox1', text)))
        else:
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
    host = family.hostname(code)
    name = re.sub(' ', '_', name)
    if not '%' in name and do_quote: # It should not have been done yet
        if name != urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    address = family.get_address(code, name)
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
        if key in family.langs.iterkeys():
            result.append(key)
    for key in family.seriouslangs:
        if key not in result:
            result.append(key)
    return result

def allpages(start = '%21%200'):
    """Iterate over all Wikipedia pages in the home language, starting
       at the given page."""
    start = link2url(start, code = mylang)
    m=0
    while 1:
        text = getPage(mylang, family.allpagesname(mylang, start),
                       do_quote=0, do_edit=0)
        #print text
        if family.version(mylang)=="1.2":
            R = re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        else:
            R = re.compile('title =\"(.*?)\"')
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
    for code in family.langs:
        m=re.search(r'\[\['+code+':([^\]]*)\]\]', text)
        if m:
            if m.group(1):
                t=m.group(1)
                if '|' in t:
                    t=t[:t.index('|')]
                if incode == 'eo':
                    t=t.replace('xx','x')
                if code in family.obsolete:
                    print "ERROR: ignoring link to obsolete language %s:%s"%(
                        code, repr(t))
                elif not t:
                    print "ERROR: ignoring impossible link to %s:%s"%(code,m.group(1))
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
    for code in family.langs:
        text = re.sub(r'\[\['+code+':([^\]]*)\]\]', '', text)
    m=re.search(r'\[\[([a-z][a-z]):([^\]]*)\]\]', text)
    if m:
        print "WARNING: Link to unknown language %s name %s"%(m.group(1), repr(m.group(2)))
    return normalWhitespace(text)

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
    if mylang in family.interwiki_putfirst:
        #In this case I might have to change the order
        ar2 = []
        for code in family.interwiki_putfirst[mylang]:
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

def normalWhitespace(text):
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

# Categories

def getCategoryLinks(text, code):
    """Returns a list of category links.
       in the form {code:pagename}. Do not call this routine directly, use
       PageLink objects instead"""
    result = []
    ns = family.category_namespaces(code)
    for prefix in ns:
        R = re.compile(r'\[\['+prefix+':([^\]]*)\]\]')
        for t in R.findall(text):
            if t:
                if code == 'eo':
                    t = t.replace('xx','x')
                t = t.capitalize()
                result.append(ns[0]+':'+t)
            else:
                print "ERROR: empty category link"
    return result

def removeCategoryLinks(text, code):
    """Given the wiki-text of a page, return that page with all category
       links removed. """
    ns = family.category_namespaces(code)
    for prefix in ns:
        text = re.sub(r'\[\['+prefix+':([^\]]*)\]\]', '', text)
    return normalWhitespace(text)

def replaceCategoryLinks(oldtext, new, code = None):
    """Replace the category links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a list of category pagelink objects.
    """
    if code is None:
        code = mylang
    s = categoryFormat(new)
    s2 = removeCategoryLinks(oldtext, code)
    if s:
        if mylang in config.category_atbottom:
            newtext = s2 + config.category_text_separator + s
        else:
            newtext = s + config.category_text_separator + s2
    else:
        newtext = s2
    return newtext
    
def categoryFormat(links):
    """Create a suitable string encoding all category links for a wikipedia
       page.

       'links' should be a list of category pagelink objects.

       The string is formatted for inclusion in mylang.
    """
    if not links:
        return ''
    s = []
    for pl in links:
        s.append(pl.aslocallink())
    if mylang in config.category_on_one_line:
        sep = ' '
    else:
        sep = '\r\n'
    s.sort()
    s=sep.join(s) + '\r\n'
    return s 

# end of category specific code

def code2encoding(code):
    """Return the encoding for a specific language wikipedia"""
    return family.code2encoding(code)

def code2encodings(code):
    """Return a list of historical encodings for a specific language
       wikipedia"""
    return family.code2encodings(code)

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
        print "Using entities instead",result
        print "BUG> This is probably a bug in the robot that did not recognize an interwiki link!"
        #raise
    result = space2underline(result)
    return urllib.quote(result)

def isInterwikiLink(s):
    """Try to check whether s is in the form "xx:link" where xx: is a
       known language. In such a case we are dealing with an interwiki link."""
    if not ':' in s:
        return False
    l,k=s.split(':',1)
    if l in family.langs:
        return True
    return False

def getReferences(pl):
    host = family.hostname(pl.code())
    url = family.references_address(mylang, pl.urlname())
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

def unicode2html(x, encoding):
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
if not family.langs.has_key(mylang):
    print "Home-wikipedia from user-config.py does not exist"
    print "Defaulting to test: wikipedia"
    setMyLang('test')
    family.langs['test']='test.wikipedia.org'

# Selecting the language for a text. 'Code' is a language, 'choice'
# is a list of languages. Choose from 'choice' the language that is
# most applicable to use on the Wikipedia in language 'code'.
# The language itself is always checked first, then languages that
# have been defined to be alternatives, and finally English. If none of
# the options gives result, we just take the first language in the
# list.

def chooselang(code, choice):
    if code in choice:
        return code
    for alternative in altlang(code):
        if alternative in choice:
            return alternative
    if 'en' in choice:
        return 'en'
    return choice[1]

    
