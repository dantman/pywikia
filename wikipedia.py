# -*- coding: utf-8  -*-
"""
Library to get and put pages on a MediaWiki.
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

import config, mediawiki_messages
    
# Are we debugging this module? 0 = No, 1 = Yes, 2 = Very much so.
debug = 0

# Keep a record of whether we are logged in as a user or not
# The actual value will be set at the end of this module
loggedin = False

#
# Import the user's family. If not changed in user_config, the family
# is Wikipedia.
#
try:
    exec("import %s_family as family" % config.family)
except ImportError:
    print "Error importing the family. This probably means the family"
    print "name is mistyped in the configuration file"
    sys.exit(1)

#
# The family module used to be used as-is. However, that gave maintenance
# nightmares. Newer families are classes so that they can inherit. If a
# family is a new-style family, we must instantiate the class.
#
if hasattr(family,'Family'):
    family=family.Family()

# Set needput to True if you want write-access to the Wiki. This can be set
# to False if you want to protect yourself from programming mistakes during
# debugging.
needput = True 

# This is used during the run-time of the program to store all character
# sets encountered for each of the wikipedia languages. This allows us to
# cross-check the stored character sets in the family. Unfortunately, the
# Export feature makes this cross-check useless, so it is only used for the
# individual get-page pages.
charsets = {}

# Keep the modification time of all downloaded pages for an eventual put.
# We are not going to be worried about the memory this can take.
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
    if code in ['br','oc','th','vi','wa']:
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
    if code in ['ja','ko','minnan','za','zh','zh-cn','zh-tw']:
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

class NoNamespace(Error):
    """Wikipedia page is not in a special namespace"""

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

    def code(self):
        """The code for the language of the page this PageLink refers to,
           without :"""
        return self._code
    
    def encoding(self):
        return code2encoding(self._code)
    
    def urlname(self):
        """The name of the page this PageLink refers to, in a form suitable
           for the URL of the page."""
        return self._urlname

    def linkname(self):
        """The name of the page this PageLink refers to, in a form suitable
           for a wiki-link"""
        return self._linkname

    def catname(self):
        """The name of the page without the namespace part. Gives an error
        if the page is from the main namespace."""
        title=self.linkname()
        parts=title.split(':')
        parts=parts[1:]
        if parts==[]:
            raise NoNamespace(self)
        return ':'.join(parts)

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
            
    def ascii_linkname(self):
        """Make a link-name that contains only ascii characters"""
        # This uses a feature of code2encoding: the 'special' language
        # ascii will return the coding 'ascii'
        return url2link(self._urlname, code = self._code, incode = 'ascii')
    
    def __str__(self):
        """A simple ASCII representation of the pagelink"""
        return "%s:%s" % (self._code, self.ascii_linkname())

    def __repr__(self):
        """A more complete string representation"""
        return "%s{%s}" % (self.__class__.__name__, str(self))

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
            # Store any exceptions for later reference
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
        """True if the page exists (itself or as redirect), False if not"""
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
        """True if the page is a redirect page, False if not or not existing"""
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        return False
    
    def isEmpty(self):
        """True if the page except for language links and category links
           has less than 4 characters, False otherwise. Can return the same
           exceptions as get()
        """
        txt = self.get()
        txt = removeLanguageLinks(txt)
        txt = removeCategoryLinks(txt, self.code())
        if len(txt) < 4:
            return 1
        else:
            return 0
        
    def put(self, newtext, comment=None, watchArticle = False, minorEdit = True):
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
        """A list of interwiki links in the page. This will retrieve
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
        """A list of categories that the article is in. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of PageLink objects for each of the
           category links in the page text."""
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
           keys in hash-tables. This relies on the fact that the string
           representation of an instance can not change after the construction.
        """
        return hash(str(self))

    def links(self):
        """Gives the normal (not-interwiki, non-category) pages the page
           links to, as a list of strings
        """
        result = []
        try:
            thistxt = removeLanguageLinks(self.get())
        except IsRedirectPage:
            return
        thistxt = removeCategoryLinks(thistxt, self.code())
        w=r'([^\]\|]*)'
        Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
        for l in Rlink.findall(thistxt):
            result.append(l[0])
        return result

    def imagelinks(self):
        """Gives the wiki-images the page shows, as a list of strings
        """
        result = []
        im=family.image_namespace(self._code) + ':'
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
        """If the page is a redirect page, gives the page it redirects to
           (as a string).

           Otherwise it will raise an IsNotRedirectPage exception
        """
        try:
            self.get()
        except NoPage:
            raise NoPage(self)
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
                output(u"BUGWARNING: %s already done!" % pl.aslink())

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
                # X-es where necessary so that we can submit a changed page
                # later.
                for c in 'C','G','H','J','S','U':
                    for c2 in c,c.lower():
                        for x in 'X','x':
                            pl._contents = pl._contents.replace(c2+x,c2+x+x)

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
                #output("DBG> %s is a redirect page" % pl2.aslink())
                pl2._getexception = IsRedirectPage(m.group(1))
            else:
                if len(text)<50:
                    output(u"DBG> short text in %s:" % pl2.aslink())
                    output(text)
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
    print "Getting %d pages from %s:"%(len(pages),code)
    return GetAll(code, pages).run()
    
# Library functions

def PageLinksFromFile(fn):
    """Read a file of page links between double-square-brackets, and return
       them as a list of PageLink objects. 'fn' is the name of the file that
       should be read."""
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
        if debug:
            print "k =", k
            print "v =", v
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

def putPage(code, name, text, comment = None, watchArticle = False, minorEdit = True, newPage = False):
    """Upload 'text' on page 'name' to the 'code' language wikipedia.
       Use of this routine can normally be avoided; use PageLink.put
       instead.
    """
    import httplib
    # Check whether we are not too quickly after the previous putPage, and
    # wait a bit until the interval is acceptable
    put_throttle()
    # Which web-site host are we submitting to?
    host = family.hostname(code)
    # Get the address of the page on that host.
    address = family.put_address(code, space2underline(name))
    # If no comment is given for the change, use the default
    if comment is None:
        comment=action
    # Prefix the comment with the user name if the user is not logged in.
    if not loggedin or code != mylang:
        comment = username + ' - ' + comment
    # Use the proper encoding for the comment
    comment = comment.encode(code2encoding(code))
    try:
        # Encode the text into the right encoding for the wiki
        text = forCode(text, code)
        predata = [
            ('wpSave', '1'),
            ('wpSummary', comment),
            ('wpTextbox1', text)]
        # Except if the page is new, we need to supply the time of the
        # previous version to the wiki to prevent edit collisions
        if newPage and newPage != '0':
            predata.append(('wpEdittime', ''))
        else:
            predata.append(('wpEdittime', edittime[code, link2url(name, code)]))
        # Pass the minorEdit and watchArticle arguments to the Wiki.
        if minorEdit and minorEdit != '0':
            predata.append(('wpMinoredit', '1'))
        if watchArticle and watchArticle != '0':
            predata.append(('wpWatchthis', '1'))
        # Encode all of this into a HTTP request
        data = urlencode(tuple(predata))
    
    except KeyError:
        print edittime
	raise
    if debug:
        print text
        print address
        print data
        return None, None, None
    output(url2unicode("Changing page %s:%s"%(code,name), language = code))
    # Submit the prepared information
    conn = httplib.HTTPConnection(host)

    conn.putrequest("POST", address)

    conn.putheader('Content-Length', str(len(data)))
    conn.putheader("Content-type", "application/x-www-form-urlencoded")
    conn.putheader("User-agent", "RobHooftWikiRobot/1.0")
    if cookies and code == mylang:
        conn.putheader('Cookie',cookies)
    conn.endheaders()
    conn.send(data)

    # Prepare the return values
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if data != '':
        output(data, decoder = myencoding())
    return response.status, response.reason, data

def forCode(text, code):
    """Prepare the unicode string 'text' for inclusion into a page for
       language 'code'. All of the characters in the text should be encodable,
       otherwise this will fail! This condition is normally met, except if
       you would copy text verbatim from an UTF-8 language into a iso-8859-1
       language, and none of the robots in the package should do such things"""
    if type(text) == type(u''):
        text = text.encode(code2encoding(code))
    return text

class MyURLopener(urllib.FancyURLopener):
    version="RobHooftWikiRobot/1.0"
    
def getUrl(host,address):
    """Low-level routine to get a URL from wikipedia.

       host and address are the host and address part of a http url.

       Return value is a 2-tuple of the text of the page, and the character
       set used to encode it.
    """
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
       Do not use this directly; for 99% of the possible ideas you can
       use the PageLink object instead.

       This routine returns a unicode string containing the wiki text.
    """
    host = family.hostname(code)
    name = re.sub(' ', '_', name)
    output(url2unicode("Getting page %s:%s"%(code, name), language = code))
    # A heuristic to encode the URL into %XX for characters that are not
    # allowed in a URL.
    if not '%' in name and do_quote: # It should not have been done yet
        if name != urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    address = family.get_address(code, name)
    if do_edit:
        address += '&action=edit&printable=yes'
    if debug:
        print host, address
    # Make sure Brion doesn't get angry by waiting if the last time a page
    # was retrieved was not long enough ago.
    get_throttle()
    # Try to retrieve the page until it was successfully loaded (just in case
    # the server is down or overloaded)
    # wait for retry_idle_time minutes (growing!) between retries.
    retry_idle_time = 1
    while True:
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
                    edittime[code, link2url(name, code)] = "0"
            try:
                i1 = re.search('<textarea[^>]*>', text).end()
            except AttributeError:
                print "WARNING: No text area found on %s %s. Maybe the server is down. Retrying in %d minutes..." % (host, address, retry_idle_time)
                time.sleep(retry_idle_time * 60)
                retry_idle_time *= 2
                #retry
                continue
            i2 = re.search('</textarea>', text).start()
            if i2-i1 < 2:
                raise NoPage(code, name)
            if debug:
                print text[i1:i2]
            m = redirectRe(code).match(text[i1:i2])
            if m:
                output(u"DBG> %s is redirect to %s" % (url2unicode(name, language = code), unicode(m.group(1), code2encoding(code))))
                raise IsRedirectPage(m.group(1))
            if edittime[code, link2url(name, code)] == "0":
                print "DBG> page may be locked?!"
                #pass
                #raise LockedPage()
    
            x = text[i1:i2]
            x = unescape(x)
            while x and x[-1] in '\n ':
                x = x[:-1]
        else:
            x = text # If not editing
            
        # Convert to a unicode string
        x = unicode(x, charset)
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

def allpages(start = '!'):
    """Generator which yields all articles in the home language in
       alphanumerical order, starting at a given page. By default,
       it starts at '!', so it should yield all pages.

       The objects returned by this generator are all PageLink()s.
    """
    while 1:
        # encode Non-ASCII characters in hexadecimal format (e.g. %F6)
        start = link2url(start, code = mylang)
        # load a list which contains a series of article names (always 480?)
        returned_html = getPage(mylang, family.allpagesname(mylang, start),
                                do_quote=0, do_edit=0)
        # Try to find begin and end markers
        try:
            ibegin = returned_html.index('<!-- start content -->')
            iend = returned_html.index('<!-- end content -->')
        except ValueError:
            raise NoPage('Couldn\'t extract allpages special page. Make sure you\'re using the MonoBook skin.')
        # remove the irrelevant sections
        returned_html = returned_html[ibegin:iend]
        if family.version(mylang)=="1.2":
            R = re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        else:
            R = re.compile('title ="(.*?)"')
        # Count the number of useful links on this page
        n = 0
        for hit in R.findall(returned_html):
            # count how many articles we found on the current page
            n = n + 1
            if family.version(mylang)=="1.2":
                yield PageLink(mylang, url2link(hit, code = mylang,
                                            incode = mylang))
            else:
                yield PageLink(mylang, hit)
            # save the last hit, so that we know where to continue when we
            # finished all articles on the current page. Append a '_0' so that
            # we don't yield a page twice.
            start = hit + '%20%200'
        # A small shortcut: if there are less than 100 pages listed on this
        # page, there is certainly no next. Probably 480 would do as well,
        # but better be safe than sorry.
        if n < 100:
            break
        
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
                    output(u"ERROR: ignoring link to obsolete language %s:%s" % (code, repr(t)))
                elif not t:
                    output(u"ERROR: ignoring impossible link to %s:%s" % (code, m.group(1)))
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
        # this regex matches an interwiki link, plus trailing whitespace.
        text = re.sub(r'\[\['+code+':([^\]]*)\]\][\s]*', '', text)
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
                # remove leading / trailing spaces
                t = t.strip()
                if code == 'eo':
                    t = t.replace('xx','x')
                t = t[:1].capitalize() + t[1:]
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
    # first remove interwiki links and add them later, so that
    # interwiki tags appear below category tags if both are set
    # to appear at the bottom of the article
    interwiki_links = getLanguageLinks(oldtext)
    oldtext = removeLanguageLinks(oldtext)
    s = categoryFormat(new)
    s2 = removeCategoryLinks(oldtext, code)
    if s:
        if mylang in config.category_attop:
            newtext = s + config.category_text_separator + s2
        else:
            newtext = s2 + config.category_text_separator + s
    else:
        newtext = s2
    # now re-add interwiki links
    newtext = replaceLanguageLinks(newtext, interwiki_links)
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

def myencoding():
    """The character encoding used by the home wiki"""
    return code2encoding(mylang)

def code2encoding(code):
    """Return the encoding for a specific language wikipedia"""
    if code == 'ascii':
        return code # Special case where we do not want special characters.
    return family.code2encoding(code)

def code2encodings(code):
    """Return a list of historical encodings for a specific language
       wikipedia"""
    return family.code2encodings(code)

def url2link(percentname, incode, code):
    """Convert a url-name of a page into a proper name for an interwiki link
       the argument 'incode' specifies the encoding of the target wikipedia
       """
    result = underline2space(percentname)
    x = url2unicode(result, language = code)
    return unicode2html(x, encoding = code2encoding(incode))
    
def link2url(name, code, incode = None):
    """Convert an interwiki link name of a page to the proper name to be used
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
        name = name.replace('XX','X')
        name = name.replace('Xx','X')
        name = name.replace('xx','x')
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
        # There might be %XX encoding. Just try to decode, if that fails
        # we must ignore the % sign and it is apparently in the title.
        try:
            name = url2unicode(name, language = code)
        except UnicodeError:
            name = html2unicode(name, language = code, altlanguage = incode)
    else:
        name = html2unicode(name, language = code, altlanguage = incode)

    #print "DBG>",repr(name)
    # Remove spaces from beginning and the end
    name = name.strip()
    # Standardize capitalization
    if name:
        if not code in family.nocapitalize:
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

def getReferences(pl, follow_redirects = True):
    host = family.hostname(pl.code())
    url = family.references_address(mylang, pl.urlname())
    output('Getting references to %s:%s' % (pl.code(), pl.linkname()))
    txt, charset = getUrl(host,url)
    # remove brackets which would disturb the regular expression cascadedListR 
    txt = txt.replace('<a', 'a')
    txt = txt.replace('</a', '/a')
    txt = txt.replace('<li', 'li')
    txt = txt.replace('</li', 'li')
    if not follow_redirects:
        # remove these links from HTML which are in an unordered
        # list at level > 1.
        cascadedListR = re.compile(r"(.*<ul>[^<]*)<ul>[^<]*<\/ul>([^<]*</\ul>.*)")
        endR = re.compile(r"</ul>")
        # current index in txt string
        pos = 0
        while cascadedListR.search(txt):
            m = cascadedListR.search(txt)
            txt = m.group(1) + m.group(2)
    Rref = re.compile('li>a href.*="([^"]*)"')
    x = Rref.findall(txt)
    x.sort()
    # Remove duplicates
    for i in range(len(x)-1, 0, -1):
        if x[i] == x[i-1]:
            del x[i]
    return x

def deletePage(pl, reason = None, prompt = True):
    """Deletes page pl from the wiki. Requires administrator status. If
       reason is None, asks for a reason. If prompt is True, asks the user
       if he wants to delete the page.
    """
    # TODO: Find out if bot is logged in with an admin account, raise exception
    # or show error message otherwise
    # TODO: Find out if deletion was successful or e.g. if file has already been
    # deleted by someone else

    # taken from lib_images.py and modified
    def post_multipart(host, selector, fields):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return the server's response page.
        """
        import httplib
        content_type, body = encode_multipart_formdata(fields)
        h = httplib.HTTP(host)
        h.putrequest('POST', selector)
        h.putheader('content-type', content_type)
        h.putheader('content-length', str(len(body)))
        h.putheader("User-agent", "RobHooftWikiRobot/1.0")
        h.putheader('Host', host)
        h.putheader('Cookie', cookies)
        h.endheaders()
        h.send(body)
        errcode, errmsg, headers = h.getreply()
        return h.file.read()
    
    # taken from lib_images.py and modified
    def encode_multipart_formdata(fields):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    if reason == None:
        reason = input('Please enter a reason for the deletion:', myencoding())
    answer = 'y'
    if prompt:
        answer = input('Do you want to delete %s? [y|N]' % pl.linkname())
    if answer in ['y', 'Y']:
        output('Deleting page %s...' % pl.linkname())
        returned_html = post_multipart(family.hostname(mylang),
                                       family.delete_address(pl.urlname()),
                                       (('wpReason', reason),
                                        ('wpConfirm', '1')))
        # check if deletion was successful
        # therefore, we need to know what the MediaWiki software says after
        # a successful deletion
        deleted_msg = mediawiki_messages.get('actioncomplete')
        deleted_msg = re.escape(deleted_msg)
        deleted_msgR = re.compile(deleted_msg)
        if deleted_msgR.search(returned_html):
            output('Deletion successful.')
        else:
            output('Deletion failed:.')
            # show debug information
            try:
                ibegin = returned_html.index('<!-- start content -->') + 22
                iend = returned_html.index('<!-- end content -->')
            except ValueError:
                # if begin/end markers weren't found, show entire HTML file
                output(returned_html, myencoding())
            else:
                # otherwise, remove the irrelevant sections
                returned_html = returned_html[ibegin:iend]
            output(returned_html, myencoding())
                                    
    
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
    # Does the input string contain non-ascii characters? In that case,
    # it is not really an url, and we do not have to unquote it....
    for c in percentname:
        if ord(c)>128:
            x=percentname
            break
    else:
        # Before removing the % encoding, make sure it is an ASCII string.
        # unquote doesn't work on unicode strings.
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
        f = open('login-data/%s-login.data' % mylang)
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


def chooselang(code, choice):
    """Selecting the language for a text. 'Code' is a language, 'choice'
       is a list of languages. Choose from 'choice' the language that is
       most applicable to use on the Wikipedia in language 'code'.
       The language itself is always checked first, then languages that
       have been defined to be alternatives, and finally English. If none of
       the options gives result, we just take the first language in the
       list.
    """
    if code in choice:
        return code
    for alternative in altlang(code):
        if alternative in choice:
            return alternative
    if 'en' in choice:
        return 'en'
    return choice[1]

def output(text, decoder = None, newline = True):
    """Works like print, but uses the encoding used by the user's console
       (console_encoding in the configuration file) instead of ASCII. If
       decoder is None, text should be a unicode string. Otherwise it
       should be encoded in the given encoding."""
    # If a character can't be displayed, it will be replaced with a
    # question mark.
    if decoder:
        text = unicode(text, decoder)
    elif type(text) != type(u''):
        print "DBG> BUG: Non-unicode passed to wikipedia.output without decoder!" 	 
        import traceback 	 
        print traceback.print_stack() 	 
        print "DBG> Attempting to recover, but please report this problem"
        try:
            text = unicode(text, 'utf-8')
        except UnicodeDecodeError:
            text = unicode(text, 'iso8859-1')
    if newline:
        print text.encode(config.console_encoding, 'replace')
    else:
        # comma means 'don't print newline after question'
        print text.encode(config.console_encoding, 'replace'),

def input(question, encode = False, decoder=None):
    """Works like raw_input(), but returns a unicode string instead of ASCII.
       if encode is True, it will encode the entered string into a format
       suitable for the local wiki (utf-8 or iso8859-1). Otherwise it will
       return Unicode. If decoder is None, question should be a unicode
       string. Otherwise it should be encoded in the given encoding.
       Unlike raw_input, this function automatically adds a space after the
       question.
    """
    output(question, decoder=decoder, newline=False)
    text = raw_input()
    text = unicode(text, config.console_encoding)
    if encode:
        text = text.encode(myencoding())
    return text
