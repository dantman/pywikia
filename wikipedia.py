# Library to get and put pages on Wikipedia
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.
import re,urllib,codecs,sys

# known wikipedia languages
langs = {'en':'www.wikipedia.org', # English
         'pl':'pl.wikipedia.org', # Polish
         'da':'da.wikipedia.org', # Danish
         'sv':'sv.wikipedia.org', # Swedish
         'zh':'zh.wikipedia.org', # Chinese
         'eo':'eo.wikipedia.org', # Esperanto
         'nl':'nl.wikipedia.org', # Dutch
         'de':'de.wikipedia.org', # German
         'fr':'fr.wikipedia.org', # French
         'es':'es.wikipedia.org', # Spanish
         'cs':'cs.wikipedia.org', # Czech
         'ru':'ru.wikipedia.org', # Russian
         'ja':'ja.wikipedia.org', # Japanese
         'sl':'sl.wikipedia.org', # Slovenian
         'ko':'ko.wikipedia.org', # Korean
         'hu':'hu.wikipedia.org', # Hungarian
         'el':'el.wikipedia.org',
         'bs':'bs.wikipedia.org',
	 'he':'he.wikipedia.org', # Hebrew
         'hi':'hi.wikipedia.org', # Hindi
         'nds':'nds.wikipedia.org', # Nedersaksisch
         'it':'it.wikipedia.com', # Italian
         'no':'no.wikipedia.com', # Norwegian
         'pt':'pt.wikipedia.com', # Portuguese
         'af':'af.wikipedia.com', # Afrikaans
         'fy':'fy.wikipedia.com', # Frysk
         'la':'la.wikipedia.com', # Latin
         'ca':'ca.wikipedia.com', # Catalan
         'fi':'fi.wikipedia.com', # Finnish
         'ia':'ia.wikipedia.com', # Interlingua
         'et':'et.wikipedia.com', 
         'eu':'eu.wikipedia.com',
         #'simple':'simple.wikipedia.com', # Simplified english
         #'test':'test.wikipedia.org',
         }

charsets = {}

# Get the name of the user for submit messages
try:
    f=open('username.dat')
    username=f.readline()[:-1]
    f.close()
except IOError:
    print >> sys.stderr, "Please make a file username.dat with your name in there"
    sys.exit(1)

# Default action
action = username+' - Wikipedia python library'

debug = 0

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
    """Wikipedia page does not exist"""

#
class PageLink:
    def __init__(self,code,name=None,urlname=None,linkname=None,incode=None):
        self._incode=incode
        self._code=code
        if linkname is None and urlname is None and name is not None:
            # Clean up the name, it can come from anywhere.
            name=name.strip()
            self._urlname=link2url(name,self._code)
            self._linkname=url2link(self._urlname,code=self._code,incode=self._incode)
        elif linkname is not None:
            # We do not trust a linkname either....
            name=linkname.strip()
            self._urlname=link2url(name,self._code)
            self._linkname=url2link(self._urlname,code=self._code,incode=self._incode)
        elif urlname is not None:
            self._urlname=urlname
            self._linkname=url2link(urlname,code=self._code,incode=self._incode)

    def urlname(self):
        return self._urlname

    def linkname(self):
        return self._linkname

    def code(self):
        return self._code
    
    def __str__(self):
        return "%s:%s"%(self._code,url2link(self._urlname,code=self._code,incode='ascii'))

    def __repr__(self):
        return "PageLink{%s}"%str(self)
    
    def get(self):
        return getPage(self.code(),self.urlname())

    def put(self,newtext,comment=None):
        return putPage(self.code(),self.urlname(),newtext,comment)

    def interwiki(self):
        result=[]
        for newcode,newname in getLanguageLinks(self.get(),incode=self.code()).iteritems():
            result.append(self.__class__(newcode,linkname=newname))
        return result

    def __cmp__(self,other):
        #print "__cmp__",self,other
        if not self.code()==other.code():
            return cmp(self.code(),other.code())
        u1=html2unicode(self.linkname(),language=self.code())
        u2=html2unicode(other.linkname(),language=other.code())
        #print "__cmp__",repr(u1),repr(u2)
        return cmp(u1,u2)

    def __hash__(self):
        return hash(str(self))
    
# Library functions
def unescape(s):
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

def urlencode(query):
    l=[]
    for k, v in query:
        k = urllib.quote(str(k))
        v = urllib.quote(str(v))
        l.append(k + '=' + v)
    return '&'.join(l)

def space2underline(name):
    return name.replace(' ','_')

def underline2space(name):
    return name.replace('_',' ')

def putPage(code, name, text, comment=None):
    """Upload 'text' on page 'name' to the 'code' language wikipedia."""
    import httplib
    host = langs[code]
    if host[-4:] == '.com':
        raise Error("Cannot put pages on a .com wikipedia")
    address = '/w/wiki.phtml?title=%s&action=submit'%space2underline(name)
    if comment is None:
        comment=action
    try:
        data = urlencode((
            ('wpSummary', comment),
            ('wpMinoredit', '1'),
            ('wpSave', '1'),
            ('wpEdittime', edittime[code,space2underline(name)]),
            ('wpTextbox1', text)))
    except KeyError:
        print edittime
	raise
    if debug:
        print text
        print address
        print data
        #return None, None, None
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = httplib.HTTPConnection(host)
    conn.request("POST", address, data, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return response.status, response.reason, data

def getUrl(host,address):
    uo=urllib.FancyURLopener()
    f=uo.open('http://%s%s'%(host,address))
    text=f.read()
    ct=f.info()['Content-Type']
    R=re.compile('charset=([^\'\"]+)')
    m=R.search(ct)
    if m:
        charset=m.group(1)
    else:
        charset=None
    return text,charset
    
def getPage(code, name, do_edit=1, do_quote=1):
    """Get the contents of page 'name' from the 'code' language wikipedia"""
    host = langs[code]
    if host[-4:]=='.com':
        # Old algorithm
        name = re.sub('_', ' ', name)
        n=[]
        for x in name.split():
            n.append(x[0].capitalize()+x[1:])
        name='_'.join(n)
        #print name
    else:
        name = re.sub(' ', '_', name)
    if not '%' in name and do_quote: # It should not have been done yet
        if name!=urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    if host[-4:] == '.org': # New software
        address = '/w/wiki.phtml?title='+name
        if do_edit:
            address += '&action=edit'
    elif host[-4:]=='.com': # Old software
        if not do_edit:
            raise "can not skip edit on old-software wikipedia"
        address = '/wiki.cgi?action=edit&id='+name
    if debug:
        print host,address
    text,charset = getUrl(host,address)
    if do_edit:
        if debug:
            print "Raw:",len(text),type(text),text.count('x')
        if charset is None:
            print "WARNING: No character set found"
        else:
            # Store character set for later reference
            if charsets.has_key(code):
                assert charsets[code]==charset
            charsets[code]=charset
            if code2encoding(code).lower()!=charset.lower():
                raise ValueError("code2encodings has wrong charset for %s. It should be %s"%(code,charset))
            
        if debug>1:
            print repr(text)
        m = re.search('value="(\d+)" name=\'wpEdittime\'',text)
        if m:
            edittime[code,space2underline(name)]=m.group(1)
        else:
            m = re.search('value="(\d+)" name="wpEdittime"',text)
            if m:
                edittime[code,name]=m.group(1)
            else:
                edittime[code,name]=0
        try:
            i1 = re.search('<textarea[^>]*>',text).end()
        except AttributeError:
            #print "No text area.",host,address
            #print repr(text)
            raise LockedPage(text)
        i2 = re.search('</textarea>',text).start()
        if i2-i1 < 2: # new software
            raise NoPage()
        if debug:
            print text[i1:i2]
        if text[i1:i2] == 'Describe the new page here.\n': # old software
            raise NoPage()
        Rredirect=re.compile(r'\#redirect:? *\[\[(.*?)\]\]',re.I)
        m=Rredirect.match(text[i1:i2])
        if m:
            raise IsRedirectPage(m.group(1))
        assert edittime[code,name]!=0 or host[-4:]=='.com', "No edittime on non-empty page?! %s:%s\n%s"%(code,name,text)

        x=text[i1:i2]
        x=unescape(x)
    else:
        x=text # If not editing
        
    if charset=='utf-8':
        # Make it to a unicode string
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('utf-8')
        try:
            x,l=decode_func(x)
        except UnicodeError:
            print code,name
            print repr(x)
            raise 
        # Convert the unicode characters to &# references, and make it ascii.
        x=str(UnicodeToAsciiHtml(x))
    return x

def languages(first=[]):
    """Return a list of language codes for known wikipedia servers"""
    result=[]
    for key in first:
        if key in langs.iterkeys():
            result.append(key)
    for key in langs.iterkeys():
        if key not in result:
            result.append(key)
    return result

def allnlpages(start='%20%200'):
    import sys
    start=link2url(start,code='nl')
    m=0
    while 1:
        text=getPage('nl','Speciaal:Allpages&printable=yes&from=%s'%start,do_quote=0,do_edit=0)
        #print text
        R=re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        n=0
        for hit in R.findall(text):
            if not ':' in hit:
                if not hit in ['Hoofdpagina','In_het_nieuws']:
                    n=n+1
                    yield url2link(hit,code='nl',incode='nl')
                    start=hit+'%20%200'
        if n<100:
            break
        m=m+n
        sys.stderr.write('AllNLPages: %d done; continuing from "%s";\n'%(m,url2link(start,code='nl',incode='ascii')))

# Part of library dealing with interwiki links

def getLanguageLinks(text,incode=None):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}"""
    result = {}
    for code in langs:
        m=re.search(r'\[\['+code+':([^\]]*)\]\]', text)
        if m:
            if m.group(1):
                t=m.group(1)
                if '|' in t:
                    t=t[:t.index('|')]
                if incode=='eo':
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
    s=[]
    ar=links.keys()
    ar.sort()
    for code in ar:
        s.append('[[%s:%s]]'%(code, links[code]))
    return ' '.join(s)+'\r\n'

def code2encoding(code):
    if code in ['meta','ru','eo','ja','zh','hi','he','hu','pl','ko','cs']:
        return 'utf-8'
    return 'iso-8859-1'

def code2encodings(code):
    # Historic compatibility
    if code=='pl':
        return 'utf-8','iso-8859-2'
    if code=='ru':
        return 'utf-8','iso-8859-5'
    if code=='cs':
        return 'utf-8','iso-8859-1'
    return code2encoding(code),
    
def url2link(percentname,incode,code):
    """Convert a url-name of a page into a proper name for an interwiki link
       the optional argument 'into' specifies the encoding of the target wikipedia
       """
    result=underline2space(percentname)
    x=url2unicode(result,language=code)
    if code2encoding(incode)==code2encoding(code):
        #print "url2link",repr(x),"same encoding"
        return unicode2html(x,encoding=code2encoding(code))
    else:
        #print "url2link",repr(x),"different encoding"
        return unicode2html(x,encoding='ascii')
    
def link2url(name,code):
    """Convert a interwiki link name of a page to the proper name to be used
       in a URL for that page. code should specify the language for the link"""
    if '%' in name:
        name=url2unicode(name,language=code)
    else:
        name=html2unicode(name,language=code)
    # Remove spaces from beginning and the end
    name=name.strip()
    # Standardize capitalization
    if name:
        name=name[0].upper()+name[1:]
    try:
        result=str(name.encode(code2encoding(code)))
    except UnicodeError:
        print "Cannot convert %s into a URL for %s"%(repr(name),code)
        raise
    result=space2underline(result)
    return urllib.quote(result)

######## Unicode library functions ########

def UnicodeToAsciiHtml(s):
    html=[]
    i=0
    for c in s:
        cord=ord(c)
        #print cord,
        if cord < 128:
            html.append(c)
        else:
            html.append('&#%d;'%cord)
    #print
    return ''.join(html)

def url2unicode(percentname,language):
    x=urllib.unquote(percentname)
    for encoding in code2encodings(language):
        try:
            encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
            x,l=decode_func(x)
            return x
        except UnicodeError:
            pass
    raise UnicodeError("Could not decode %s"%repr(percentname))

def unicode2html(x,encoding='latin1'):
    # We have a unicode string. We can attempt to encode it into the desired
    # format, and if that doesn't work, we encode the unicode into html #
    # entities.
    try:
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
        x,l=encode_func(x)
        #print "unicode2html",x
    except UnicodeError:
        x=UnicodeToAsciiHtml(x)
    return str(x)
    
def removeEntity(name):
    import re,htmlentitydefs
    Rentity=re.compile(r'&([A-Za-z]+);')
    result=''
    i=0
    while i<len(name):
        m=Rentity.match(name[i:])
        if m:
            if htmlentitydefs.entitydefs.has_key(m.group(1)):
                result=result+htmlentitydefs.entitydefs[m.group(1)]
                i=i+m.end()
            else:
                result=result+name[i]
                i=i+1
        else:
            result=result+name[i]
            i=i+1
    return result

def unicodeName(name,language):
    for encoding in code2encodings(language):
        try:
            return unicode(name,encoding)
        except UnicodeError:
            continue
    print language,name
    raise "Would be encoding into local, probably a bug"
    #return unicode(name,code2encoding(inlanguage))
    
def html2unicode(name,language):
    name=removeEntity(name)
    name=unicodeName(name,language)

    import re
    Runi=re.compile('&#(\d+);')
    result=u''
    i=0
    while i<len(name):
        m=Runi.match(name[i:])
        if m:
            result=result+unichr(int(m.group(1)))
            i=i+m.end()
        else:
            try:
                result=result+name[i]
                i=i+1
            except UnicodeDecodeError:
                print repr(name)
                raise
    return result
