# Library to get and put pages on Wikipedia
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.
import re,urllib,codecs

# known wikipedia languages
langs = {'en':'www.wikipedia.org',
         'pl':'pl.wikipedia.org',
         'da':'da.wikipedia.org',
         'sv':'sv.wikipedia.org',
         'zh':'zh.wikipedia.org',
         'eo':'eo.wikipedia.org',
         'nl':'nl.wikipedia.org',
         'de':'de.wikipedia.org',
         'fr':'fr.wikipedia.org',
         'es':'es.wikipedia.org',
         'cs':'cs.wikipedia.org',
         'ru':'ru.wikipedia.org',
         'ja':'ja.wikipedia.org',
         'sl':'sl.wikipedia.org',
         'ko':'ko.wikipedia.org',
         'hu':'hu.wikipedia.org',
         'el':'el.wikipedia.org',
         'it':'it.wikipedia.com',
         'no':'no.wikipedia.com',
         'pt':'pt.wikipedia.com',
         'af':'af.wikipedia.com',
         'fy':'fy.wikipedia.com',
         'la':'la.wikipedia.com',
         'ca':'ca.wikipedia.com',
         'fi':'fi.wikipedia.com',
         'ia':'ia.wikipedia.com',
         'et':'et.wikipedia.com',
         'eu':'eu.wikipedia.com',
         'simple':'simple.wikipedia.com',
         #'test':'test.wikipedia.org',
         }

charsets = {}

action = 'Rob Hooft - Wikipedia python library'

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
            n.append(x.capitalize())
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
        x,l=decode_func(x)
        # Convert the unicode characters to &# references, and make it ascii.
        x=str(UnicodeToHtml(x))
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
    wikipedia.link2url(start)
    m=0
    while 1:
        text=wikipedia.getPage('nl','Speciaal:Allpages&printable=yes&from=%s'%start,do_quote=0,do_edit=0)
        #print text
        R=re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        n=0
        for hit in R.findall(text):
            if not ':' in hit:
                if not hit in ['Hoofdpagina','In_het_nieuws']:
                    n=n+1
                    yield wikipedia.url2link(hit)
                    start=hit+'%20%200'
        if n<100:
            break
        m=m+n
        sys.stderr.write('AllNLPages: %d done; continuing from "%s";\n'%(m,wikipedia.link2url(start)))

# Part of library dealing with interwiki links

def getLanguageLinks(text):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}"""
    result = {}
    for code in langs:
        m=re.search(r'\[\['+code+':([^\]]*)\]\]', text)
        if m:
            if m.group(1):
                result[code] = m.group(1)
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
    s=''
    ar=links.keys()
    ar.sort()
    for code in ar:
        s = s + '[[%s:%s]]'%(code, links[code])
    return s+'\r\n'

def url2link(percentname,into='latin1'):
    """Convert a url-name of a page into a proper name for an interwiki link
       the optional argument 'into' specifies the encoding of the target wikipedia
       """
    result=underline2space(percentname)
    x=url2unicode(result)
    if into=='latin1':
        return unicode2latin1(x)
    else:
        raise "Unknown encoding"
    
def link2url(name):
    """Convert a interwiki link name of a page to the proper name to be used
       in a URL for that page"""
    import urllib
    name=name[0].upper()+name[1:]
    name=name.strip()
    if '%' in name:
        name=url2unicode(name)
    else:
        import urllib
        name=html2unicode(name)
    try:
        result=str(name.encode('latin1'))
    except UnicodeError:
        result=str(name.encode('utf-8'))
    result=space2underline(result)
    return urllib.quote(result)

######## Unicode library functions ########

def UnicodeToHtml(s):
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

def url2unicode(percentname):
    x=urllib.unquote(percentname)
    try:
        # Try to interpret the result as utf-8?
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('utf-8')
        x,l=decode_func(x)
    except UnicodeError:
        # Apparently it was latin1?
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('latin1')
        x,l=decode_func(x)
    return x

def unicode2latin1(x):
    # We have a unicode string. We can attempt to make it latin1, and
    # if that doesn't work, we encode the unicode into html # entities.
    try:
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('latin1')
        x,l=encode_func(x)
    except UnicodeError:
        x=UnicodeToHtml(x)
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

def html2unicode(name):
    name=removeEntity(name)
    import re
    if not '&#' in name:
        return unicode(name,'latin1')
    Runi=re.compile('&#(\d+);')
    result=u''
    i=0
    while i<len(name):
        m=Runi.match(name[i:])
        if m:
            result=result+unichr(int(m.group(1)))
            i=i+m.end()
        else:
            result=result+name[i]
            i=i+1
    return result
